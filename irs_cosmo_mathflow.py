
"""
IRS_COSMO / IRS_GRAV MathFlow
=============================

Minimal Python models implementing the basic calculations used in the
IRS_COSMO + IRS_GRAV v1.0 work.

Zawartość:
----------
1. Decomposition of observational H(z) data into:
   - baryonic contribution Ω_b (1+z)^3
   - "extra" term Ω_extra(z) = Ω_I(z) + Ω_Φ(z)

2. Toy model of galactic rotation curves in IRS_GRAV (dimensionless):
   - baryonic exponential disk
   - informational contribution with ρ_I ∝ 1/r^2 → M_I(r) ∝ r

3. Physical IRS_GRAV galactic model (z jednostkami):
   - Milky-Way-like galaxy
   - calibration of α from v(r₀)
   - rotation curves: baryons vs baryons + IRS
   - effective informational density ρ_I(r)

4. (Optional / experimental) toy IRS-FLRW integrator skeleton.

Zależności (minimalne):
    numpy, pandas, matplotlib

Użycie (z linii poleceń):

    python irs_cosmo_mathflow.py

albo z innego skryptu / notebooka:

    import irs_cosmo_mathflow as irs
    df = irs.compute_Hz_decomposition()
    irs.plot_Hz(df)
    irs.plot_Ez2_decomposition(df)
    irs.demo_galaxy_physical()

Autor: SCH (concept), IRS_COSMO / IRS_GRAV project
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Dict, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------
# 1. Observational H(z) decomposition
# ---------------------------------------------------------------------

# Uproszczony zestaw punktów H(z) (cosmic chronometers) – wartości
# orientacyjne, wystarczające do proof-of-concept.
OHD_DATA: List[Dict[str, float]] = [
    {"z": 0.07, "H": 69.0, "sigma_H": 19.6},
    {"z": 0.12, "H": 68.6, "sigma_H": 26.2},
    {"z": 0.17, "H": 83.0, "sigma_H": 8.0},
    {"z": 0.20, "H": 72.9, "sigma_H": 29.6},
    {"z": 0.27, "H": 77.0, "sigma_H": 14.0},
    {"z": 0.28, "H": 88.8, "sigma_H": 36.6},
    {"z": 0.40, "H": 95.0, "sigma_H": 17.0},
    {"z": 0.43, "H": 86.5, "sigma_H": 3.7},
    {"z": 0.48, "H": 97.0, "sigma_H": 62.0},
    {"z": 0.88, "H": 90.0, "sigma_H": 40.0},
]


@dataclass
class CosmologyParams:
    """Podstawowe parametry kosmologiczne dla analizy H(z)."""

    H0: float = 67.4   # km/s/Mpc (Planck-like)
    Omega_b: float = 0.049  # baryons (Planck-like)


def get_Hz_dataframe() -> pd.DataFrame:
    """Zwróć obserwacyjne H(z) jako DataFrame."""
    df = pd.DataFrame(OHD_DATA)
    return df.sort_values("z").reset_index(drop=True)


def compute_Hz_decomposition(
    cosmo: CosmologyParams | None = None
) -> pd.DataFrame:
    """Policz E(z)^2, baryonic term i Ω_extra dla każdego punktu H(z).

    Zwracane kolumny:

        E_z          = H / H0
        E_z2         = (H / H0)^2
        Omega_b_term = Ω_b (1 + z)^3
        Omega_extra  = E_z2 - Omega_b_term
    """
    if cosmo is None:
        cosmo = CosmologyParams()

    df = get_Hz_dataframe().copy()
    H0 = cosmo.H0
    Omega_b = cosmo.Omega_b

    df["E_z"] = df["H"] / H0
    df["E_z2"] = df["E_z"] ** 2
    df["Omega_b_term"] = Omega_b * (1.0 + df["z"]) ** 3
    df["Omega_extra"] = df["E_z2"] - df["Omega_b_term"]
    return df


def plot_Hz(df: pd.DataFrame, show: bool = True, savepath: str | None = None) -> None:
    """Wykres H(z) z błędami."""
    plt.figure()
    plt.errorbar(df["z"], df["H"], yerr=df["sigma_H"], fmt="o")
    plt.xlabel("Redshift z")
    plt.ylabel("H(z) [km/s/Mpc]")
    plt.title("Observed H(z) points")
    plt.grid(True, alpha=0.3)
    if savepath is not None:
        plt.savefig(savepath, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close()


def plot_Ez2_decomposition(
    df: pd.DataFrame, show: bool = True, savepath: str | None = None
) -> None:
    """Wykres E(z)^2, baryonic term i Ω_extra(z) na jednym wykresie."""
    plt.figure()
    plt.plot(df["z"], df["E_z2"], marker="o", label=r"E(z)$^2$")
    plt.plot(df["z"], df["Omega_b_term"], marker="s", label=r"$\Omega_b (1+z)^3$")
    plt.plot(df["z"], df["Omega_extra"], marker="^", label=r"$\Omega_{\mathrm{extra}}(z)$")
    plt.xlabel("Redshift z")
    plt.ylabel("Dimensionless density-like terms")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.title("Decomposition of E(z)$^2$ into baryons and extra component")
    if savepath is not None:
        plt.savefig(savepath, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close()


# ---------------------------------------------------------------------
# 2. Toy galactic rotation curves in IRS_GRAV (dimensionless)
# ---------------------------------------------------------------------

@dataclass
class GalaxyParamsDimless:
    """Parametry dla bezwymiarowego modelu galaktyki IRS_GRAV."""

    G: float = 1.0    # toy gravitational constant
    M0: float = 1.0   # baryonic mass scale
    r_d: float = 3.0  # disk scale length (arbitrary units)
    alpha: float = 0.15  # strength of informational mass term M_I = alpha * r


def baryonic_mass_profile_dimless(r: np.ndarray, params: GalaxyParamsDimless) -> np.ndarray:
    """Bezwymiarowy profil baryonic mass (exponential disk)."""
    return params.M0 * (1.0 - np.exp(-r / params.r_d))


def informational_mass_profile_dimless(r: np.ndarray, params: GalaxyParamsDimless) -> np.ndarray:
    """Bezwymiarowy profil M_I(r) = alpha * r."""
    return params.alpha * r


def rotation_curves_dimless(
    r: np.ndarray, params: GalaxyParamsDimless
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Policz bezwymiarowe krzywe rotacji.

    Zwraca (M_b, M_I, v_b, v_tot).
    """
    G = params.G
    M_b = baryonic_mass_profile_dimless(r, params)
    M_I = informational_mass_profile_dimless(r, params)
    v_b = np.sqrt(G * M_b / r)
    v_tot = np.sqrt(G * (M_b + M_I) / r)
    return M_b, M_I, v_b, v_tot


def plot_rotation_curves_dimless(
    params: GalaxyParamsDimless | None = None,
    r_min: float = 0.5,
    r_max: float = 25.0,
    n_points: int = 200,
    show: bool = True,
    savepath: str | None = None,
) -> None:
    """Wygeneruj i narysuj bezwymiarowe krzywe rotacji."""
    if params is None:
        params = GalaxyParamsDimless()

    r = np.linspace(r_min, r_max, n_points)
    _, _, v_b, v_tot = rotation_curves_dimless(r, params)

    plt.figure()
    plt.plot(r, v_b, label="Baryons only (toy)")
    plt.plot(r, v_tot, label="Baryons + IRS informational term (toy)")
    plt.xlabel("Radius r [arb. units]")
    plt.ylabel("Circular velocity v(r) [arb. units]")
    plt.title("Toy galaxy rotation curves in IRS_GRAV (dimensionless)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    if savepath is not None:
        plt.savefig(savepath, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close()


# ---------------------------------------------------------------------
# 3. Physical IRS_GRAV model for a Milky-Way-like galaxy
# ---------------------------------------------------------------------

@dataclass
class GalaxyParamsPhysical:
    """
    Fizyczny model IRS_GRAV dla galaktyki spiralnej.

    Jednostki:
        r      – kpc
        M      – M_sun
        v      – km/s

    G użyte w jednostkach:
        G ≈ 4.302e-6 kpc * (km/s)^2 / M_sun
    """
    G: float = 4.302e-6         # kpc * (km/s)^2 / Msun
    M0: float = 5e10            # Msun, baryonic mass scale
    r_d: float = 3.0            # kpc, disk scale length
    r0: float = 10.0            # kpc, reference radius
    v_target: float = 220.0     # km/s, target flat velocity at r0


def M_b_physical(r: np.ndarray, params: GalaxyParamsPhysical) -> np.ndarray:
    """Baryonic cumulative mass profile in physical units."""
    return params.M0 * (1.0 - np.exp(-r / params.r_d))


def calibrate_alpha(params: GalaxyParamsPhysical) -> float:
    """
    Skalibruj α tak, by v(r0) ≈ v_target dla M_I(r) = α r.

    Rozwiązujemy równanie:
        v^2(r0) = G (M_b(r0) + α r0) / r0
    """
    G = params.G
    r0 = params.r0
    v_target = params.v_target

    Mb_r0 = M_b_physical(np.array([r0]), params)[0]
    alpha = (v_target**2 * r0 / G - Mb_r0) / r0
    return alpha


def rotation_curves_physical(
    r: np.ndarray, params: GalaxyParamsPhysical, alpha: float
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Policz krzywe rotacji w jednostkach fizycznych.

    Zwraca (M_b, M_I, v_b, v_tot).
    """
    G = params.G
    M_b = M_b_physical(r, params)
    M_I = alpha * r
    v_b = np.sqrt(G * M_b / r)
    v_tot = np.sqrt(G * (M_b + M_I) / r)
    return M_b, M_I, v_b, v_tot


def informational_density(r: float, alpha: float) -> float:
    """
    ρ_I(r) = α / (4π r²)   w jednostkach Msun/kpc³.
    """
    return alpha / (4.0 * math.pi * r**2)


def demo_galaxy_physical(
    r_min: float = 1.0,
    r_max: float = 30.0,
    n_points: int = 15,
    print_table: bool = True,
    make_plot: bool = True,
) -> None:
    """
    Demo IRS_GRAV dla galaktyki spiralnej w jednostkach fizycznych.

    - Kalibruje α z v(r0)=220 km/s przy r0=10 kpc.
    - Drukuje tabelę v_baryons vs v_total.
    - Oblicza ρ_I w okolicy r0.
    - (Opcjonalnie) rysuje krzywe rotacji.
    """
    params = GalaxyParamsPhysical()
    alpha = calibrate_alpha(params)

    r_vals = np.linspace(r_min, r_max, n_points)
    Mb_vals, MI_vals, v_b, v_tot = rotation_curves_physical(r_vals, params, alpha)

    if print_table:
        print("=== IRS_GRAV: Milky-Way-like galaxy demo ===")
        print(f"M0 = {params.M0:.2e} Msun, r_d = {params.r_d:.1f} kpc")
        print(f"Calibrated alpha = {alpha:.3e} Msun/kpc")
        print("
 r [kpc] | v_baryons [km/s] | v_total [km/s]")
        print("---------------------------------------------")
        for r, vb, vt in zip(r_vals, v_b, v_tot):
            print(f"{r:7.2f} | {vb:17.2f} | {vt:13.2f}")
        # Density at r0
        rho_I_kpc3 = informational_density(params.r0, alpha)
        rho_I_pc3 = rho_I_kpc3 / 1e9
        print("
Informational density at r0 = 10 kpc:")
        print(f"rho_I ≈ {rho_I_kpc3:.3e} Msun/kpc^3 ≈ {rho_I_pc3:.3e} Msun/pc^3")

    if make_plot:
        plt.figure()
        plt.plot(r_vals, v_b, "o-", label="Baryons only")
        plt.plot(r_vals, v_tot, "s-", label="Baryons + IRS informational term")
        plt.xlabel("Radius r [kpc]")
        plt.ylabel("Circular velocity v(r) [km/s]")
        plt.title("IRS_GRAV rotation curves (Milky-Way-like galaxy)")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()


# ---------------------------------------------------------------------
# 4. Optional toy IRS-FLRW integrator (VERY schematic)
# ---------------------------------------------------------------------

@dataclass
class IRSFLRWParams:
    """
    Parametry zabawkowego modelu IRS-FLRW.

    To jest *schemat*, nie precyzyjne narzędzie kosmologiczne.
    """

    Omega_b: float = 0.049   # baryons
    Omega_I0: float = 0.25   # "informational dark matter" at z=0 (toy)
    Omega_Phi0: float = 0.70  # "phase dark energy" at z=0 (toy)
    H0: float = 67.4          # km/s/Mpc, tylko skala


def irs_flrw_rhs(
    lam: float, y: np.ndarray, params: IRSFLRWParams
) -> np.ndarray:
    """
    Prawa strona ultra-schematu IRS-FLRW.

    Stan: y = [A, dA/dλ].
    """
    A, Adot = y
    if A <= 0:
        return np.array([Adot, 0.0])

    Omega_tot = params.Omega_b + params.Omega_I0 + params.Omega_Phi0
    effective_E2 = params.Omega_b / A**3 + (Omega_tot - params.Omega_b)
    Adot2_target = A**2 * effective_E2
    sign = 1.0 if Adot >= 0 else -1.0
    Adot_target = sign * math.sqrt(max(Adot2_target, 0.0))
    Addot = (Adot_target - Adot)
    return np.array([Adot, Addot])


def rk4_step(
    func, x: float, y: np.ndarray, h: float, params
) -> np.ndarray:
    """Klasyczny krok Runge–Kutta 4. rzędu."""
    k1 = func(x, y, params)
    k2 = func(x + 0.5 * h, y + 0.5 * h * k1, params)
    k3 = func(x + 0.5 * h, y + 0.5 * h * k2, params)
    k4 = func(x + h, y + h * k3, params)
    return y + (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


def integrate_irs_flrw(
    lam_start: float = 0.0,
    lam_end: float = 5.0,
    n_steps: int = 1000,
    A0: float = 0.1,
    Adot0: float = 0.01,
    params: IRSFLRWParams | None = None,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Integruj zabawkowy skalar A(λ)."""
    if params is None:
        params = IRSFLRWParams()

    lam_values = np.linspace(lam_start, lam_end, n_steps)
    h = lam_values[1] - lam_values[0]
    y = np.array([A0, Adot0], dtype=float)

    A_list = []
    Adot_list = []

    for lam in lam_values:
        A_list.append(y[0])
        Adot_list.append(y[1])
        y = rk4_step(irs_flrw_rhs, lam, y, h, params)

    return lam_values, np.array(A_list), np.array(Adot_list)


def plot_irs_flrw_toy(
    show: bool = True, savepath: str | None = None
) -> None:
    """Wykres zabawkowego A(λ) w IRS-FLRW."""
    lam, A, Adot = integrate_irs_flrw()
    plt.figure()
    plt.plot(lam, A, label="A(λ)")
    plt.xlabel("λ (configuration parameter)")
    plt.ylabel("A(λ) [arb. units]")
    plt.title("Toy IRS-FLRW scale factor evolution")
    plt.grid(True, alpha=0.3)
    if savepath is not None:
        plt.savefig(savepath, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close()


# ---------------------------------------------------------------------
# Main demo
# ---------------------------------------------------------------------

def main() -> None:
    """Prosty demo-run wszystkich głównych obliczeń."""
    # 1) H(z) decomposition
    cosmo = CosmologyParams()
    df = compute_Hz_decomposition(cosmo)
    print("=== H(z) decomposition (first few rows) ===")
    print(df.head())

    plot_Hz(df, show=False, savepath="IRS_Hz_observed_demo.png")
    plot_Ez2_decomposition(df, show=False, savepath="IRS_Ez2_decomposition_demo.png")
    print("Saved: IRS_Hz_observed_demo.png, IRS_Ez2_decomposition_demo.png")

    # 2) Dimensionless galaxy rotation
    params_dim = GalaxyParamsDimless()
    plot_rotation_curves_dimless(params_dim, show=False, savepath="IRS_galaxy_rotation_dimless.png")
    print("Saved: IRS_galaxy_rotation_dimless.png")

    # 3) Physical IRS_GRAV galaxy
    demo_galaxy_physical(r_min=1.0, r_max=30.0, n_points=15, print_table=True, make_plot=False)

    # 4) Toy IRS-FLRW
    plot_irs_flrw_toy(show=False, savepath="IRS_IRSFLRW_toy_demo.png")
    print("Saved: IRS_IRSFLRW_toy_demo.png")


if __name__ == "__main__":
    main()
