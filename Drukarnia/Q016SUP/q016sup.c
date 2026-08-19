#include <windows.h>
#include <ddeml.h>
#include <dos.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define APP_CLASS       "Q016SUP_REBUILD"
#define APP_TITLE       "Q016SUP - COMEXI FQ2100"
#define FICS_DIR        "C:\\Q016FICS\\"
#define DDE_SERVICE     "VIEW"
#define DDE_TOPIC       "TAGNAME"

#define IDC_LIST        100
#define IDC_REFRESH     101
#define IDC_LOAD        102
#define IDC_NEWNAME     103
#define IDC_DUP         104
#define IDC_DELETE      105
#define IDC_MINIMIZE    106
#define IDC_STATUS      107
#define IDC_MODE        108
#define TIMER_DDE       1

static HINSTANCE g_hInst;
static HWND g_hWnd;
static HWND g_hList;
static HWND g_hNewName;
static HWND g_hStatus;
static HWND g_hMode;

static DWORD g_ddeInst = 0;
static HCONV g_hConv = 0;
static HSZ g_hszService = 0;
static HSZ g_hszTopic = 0;
static FARPROC g_cbThunk = 0;
static int g_lastNew = 0;
static int g_lastRead = 0;

static HDDEDATA CALLBACK DdeCallback(UINT uType, UINT uFmt, HCONV hconv,
    HSZ hsz1, HSZ hsz2, HDDEDATA hdata, DWORD dwData1, DWORD dwData2)
{
    (void)uType; (void)uFmt; (void)hconv; (void)hsz1; (void)hsz2;
    (void)hdata; (void)dwData1; (void)dwData2;
    return (HDDEDATA)0;
}

static void SetStatus(const char *s)
{
    if (g_hStatus) SetWindowText(g_hStatus, s);
}

static int FileExists(const char *path)
{
    FILE *f = fopen(path, "rb");
    if (!f) return 0;
    fclose(f);
    return 1;
}

static void BuildPath(char *dst, const char *name)
{
    strcpy(dst, FICS_DIR);
    strcat(dst, name);
}

static int IsDos83(const char *s)
{
    int base = 0, ext = 0, dot = 0;
    unsigned char c;
    if (!s || !*s) return 0;
    while (*s) {
        c = (unsigned char)*s++;
        if (c == '.') {
            if (dot || base < 1 || base > 8) return 0;
            dot = 1;
            continue;
        }
        if (!(isalnum(c) || c == '_')) return 0;
        if (!dot) {
            if (++base > 8) return 0;
        } else {
            if (++ext > 3) return 0;
        }
    }
    return dot && ext >= 1;
}

static void RefreshJobs(void)
{
    struct find_t ff;
    unsigned rc;
    char selected[20];
    int sel;

    selected[0] = 0;
    sel = (int)SendMessage(g_hList, LB_GETCURSEL, 0, 0L);
    if (sel != LB_ERR)
        SendMessage(g_hList, LB_GETTEXT, sel, (LPARAM)(LPSTR)selected);

    SendMessage(g_hList, LB_RESETCONTENT, 0, 0L);
    rc = _dos_findfirst("C:\\Q016FICS\\*.*",
        _A_NORMAL | _A_RDONLY | _A_HIDDEN | _A_ARCH, &ff);
    while (rc == 0) {
        if (!(ff.attrib & _A_SUBDIR) && strcmp(ff.name, ".") && strcmp(ff.name, ".."))
            SendMessage(g_hList, LB_ADDSTRING, 0, (LPARAM)(LPSTR)ff.name);
        rc = _dos_findnext(&ff);
    }

    if (selected[0]) {
        int n = (int)SendMessage(g_hList, LB_GETCOUNT, 0, 0L);
        int i;
        char t[20];
        for (i = 0; i < n; ++i) {
            SendMessage(g_hList, LB_GETTEXT, i, (LPARAM)(LPSTR)t);
            if (!stricmp(t, selected)) {
                SendMessage(g_hList, LB_SETCURSEL, i, 0L);
                break;
            }
        }
    }
}

static int GetSelectedJob(char *name)
{
    int sel = (int)SendMessage(g_hList, LB_GETCURSEL, 0, 0L);
    if (sel == LB_ERR) {
        MessageBox(g_hWnd, "Wybierz zlecenie z listy.", APP_TITLE, MB_OK | MB_ICONEXCLAMATION);
        return 0;
    }
    SendMessage(g_hList, LB_GETTEXT, sel, (LPARAM)(LPSTR)name);
    return 1;
}

static int CopyJobAs(const char *srcName, const char *dstName)
{
    FILE *in, *out;
    char src[128], dst[128], line[512];
    SYSTEMTIME st;
    int lineNo = 0;

    if (!IsDos83(dstName)) {
        MessageBox(g_hWnd, "Nowa nazwa musi miec format DOS 8.3, np. 6300006.0__",
            APP_TITLE, MB_OK | MB_ICONEXCLAMATION);
        return 0;
    }

    BuildPath(src, srcName);
    BuildPath(dst, dstName);
    if (FileExists(dst)) {
        MessageBox(g_hWnd, "Plik o tej nazwie juz istnieje.", APP_TITLE,
            MB_OK | MB_ICONEXCLAMATION);
        return 0;
    }

    in = fopen(src, "rt");
    if (!in) {
        MessageBox(g_hWnd, "Nie moge otworzyc pliku wzorcowego.", APP_TITLE,
            MB_OK | MB_ICONSTOP);
        return 0;
    }
    out = fopen(dst, "wt");
    if (!out) {
        fclose(in);
        MessageBox(g_hWnd, "Nie moge utworzyc nowego pliku Q016FICS.", APP_TITLE,
            MB_OK | MB_ICONSTOP);
        return 0;
    }

    GetLocalTime(&st);
    while (fgets(line, sizeof(line), in)) {
        ++lineNo;
        if (lineNo == 1) {
            fprintf(out, "%s\n", dstName);
        } else if (lineNo == 2) {
            fprintf(out, "%02u/%02u/%02u\n", st.wDay, st.wMonth, st.wYear % 100);
        } else {
            fputs(line, out);
        }
    }
    fclose(out);
    fclose(in);

    if (lineNo < 100) {
        remove(dst);
        MessageBox(g_hWnd,
            "Plik wzorcowy nie wyglada jak kompletne zlecenie Q016. Nowy plik usunieto.",
            APP_TITLE, MB_OK | MB_ICONSTOP);
        return 0;
    }
    return 1;
}

static int DdeInitClient(void)
{
    UINT err;
    if (g_ddeInst) return 1;

    g_cbThunk = MakeProcInstance((FARPROC)DdeCallback, g_hInst);
    if (!g_cbThunk) {
        SetStatus("DDE: blad MakeProcInstance");
        return 0;
    }

    err = DdeInitialize(&g_ddeInst, (PFNCALLBACK)g_cbThunk,
        APPCMD_CLIENTONLY | CBF_SKIP_ALLNOTIFICATIONS, 0L);
    if (err != DMLERR_NO_ERROR) {
        g_ddeInst = 0;
        FreeProcInstance(g_cbThunk);
        g_cbThunk = 0;
        SetStatus("DDE: DdeInitialize - blad");
        return 0;
    }

    g_hszService = DdeCreateStringHandle(g_ddeInst, DDE_SERVICE, CP_WINANSI);
    g_hszTopic   = DdeCreateStringHandle(g_ddeInst, DDE_TOPIC, CP_WINANSI);
    return 1;
}

static void DdeDisconnectClient(void)
{
    if (g_hConv) {
        DdeDisconnect(g_hConv);
        g_hConv = 0;
    }
    if (g_ddeInst) {
        if (g_hszService) DdeFreeStringHandle(g_ddeInst, g_hszService);
        if (g_hszTopic) DdeFreeStringHandle(g_ddeInst, g_hszTopic);
        g_hszService = g_hszTopic = 0;
        DdeUninitialize(g_ddeInst);
        g_ddeInst = 0;
    }
    if (g_cbThunk) {
        FreeProcInstance(g_cbThunk);
        g_cbThunk = 0;
    }
}

static int DdeEnsureConnected(void)
{
    if (g_hConv) return 1;
    if (!DdeInitClient()) return 0;
    g_hConv = DdeConnect(g_ddeInst, g_hszService, g_hszTopic, NULL);
    if (!g_hConv) {
        SetStatus("DDE: czekam na WindowViewer VIEW|TAGNAME...");
        return 0;
    }
    SetStatus("DDE: polaczono z InTouch VIEW|TAGNAME");
    return 1;
}

static int DdePokeText(const char *item, const char *value)
{
    HSZ hItem;
    HDDEDATA h;
    if (!DdeEnsureConnected()) return 0;
    hItem = DdeCreateStringHandle(g_ddeInst, item, CP_WINANSI);
    if (!hItem) return 0;
    h = DdeClientTransaction((LPBYTE)value, (DWORD)(strlen(value) + 1),
        g_hConv, hItem, CF_TEXT, XTYP_POKE, 3000, NULL);
    DdeFreeStringHandle(g_ddeInst, hItem);
    if (!h) {
        DdeDisconnect(g_hConv);
        g_hConv = 0;
        return 0;
    }
    return 1;
}

static int DdeRequestText(const char *item, char *buf, int cb)
{
    HSZ hItem;
    HDDEDATA h;
    LPBYTE p;
    DWORD len = 0;
    if (cb < 2) return 0;
    buf[0] = 0;
    if (!DdeEnsureConnected()) return 0;
    hItem = DdeCreateStringHandle(g_ddeInst, item, CP_WINANSI);
    if (!hItem) return 0;
    h = DdeClientTransaction(NULL, 0, g_hConv, hItem, CF_TEXT,
        XTYP_REQUEST, 1200, NULL);
    DdeFreeStringHandle(g_ddeInst, hItem);
    if (!h) return 0;
    p = DdeAccessData(h, &len);
    if (p) {
        int n = (len < (DWORD)(cb - 1)) ? (int)len : cb - 1;
        memcpy(buf, p, n);
        buf[n] = 0;
        DdeUnaccessData(h);
    }
    DdeFreeDataHandle(h);
    return buf[0] != 0;
}

static int TagInt(const char *item, int *value)
{
    char b[64];
    if (!DdeRequestText(item, b, sizeof(b))) return 0;
    *value = atoi(b);
    return 1;
}

static void WakeFromInTouch(const char *why)
{
    SetWindowText(g_hMode, why);
    ShowWindow(g_hWnd, SW_SHOWNORMAL);
    BringWindowToTop(g_hWnd);
    SetActiveWindow(g_hWnd);
    RefreshJobs();
}

static void PollInTouch(void)
{
    int v;
    char st[128];

    if (!DdeEnsureConnected()) return;

    if (TagInt("nuevaficha", &v)) {
        if (v && !g_lastNew) {
            WakeFromInTouch("Tryb: NOWE ZLECENIE - wywolane z InTouch");
            DdePokeText("nuevaficha", "0");
        }
        g_lastNew = v;
    }

    if (TagInt("leerficha", &v)) {
        if (v && !g_lastRead) {
            WakeFromInTouch("Tryb: WYBOR / CZYTAJ ZLECENIE - wywolane z InTouch");
            DdePokeText("leerficha", "0");
        }
        g_lastRead = v;
    }

    if (DdeRequestText("cambioficha", st, sizeof(st))) {
        char s2[180];
        sprintf(s2, "DDE OK | cambioficha=%s", st);
        SetStatus(s2);
    }
}

static void LoadSelectedJob(void)
{
    char name[32], path[128], msg[256];
    if (!GetSelectedJob(name)) return;
    BuildPath(path, name);
    if (!FileExists(path)) {
        MessageBox(g_hWnd, "Wybrany plik juz nie istnieje.", APP_TITLE,
            MB_OK | MB_ICONSTOP);
        RefreshJobs();
        return;
    }
    sprintf(msg,
        "Zaladowac zlecenie %s do maszyny?\n\n"
        "Maszyna musi byc STOP, a postoj musi miec przypisana przyczyne.", name);
    if (MessageBox(g_hWnd, msg, APP_TITLE,
        MB_YESNO | MB_ICONQUESTION | MB_DEFBUTTON2) != IDYES) return;

    if (!DdePokeText("Bfichero", name)) {
        MessageBox(g_hWnd, "Blad DDE przy ustawianiu Bfichero.", APP_TITLE,
            MB_OK | MB_ICONSTOP);
        return;
    }
    if (!DdePokeText("cambioficha", "99")) {
        MessageBox(g_hWnd, "Bfichero ustawione, ale blad DDE przy cambioficha=99.",
            APP_TITLE, MB_OK | MB_ICONSTOP);
        return;
    }
    sprintf(msg,
        "Komenda przekazana do InTouch.\n\nBfichero=%s\ncambioficha=99\n\n"
        "Dalej pracuje oryginalna sekwencja InTouch 99->1->2->3->4->5->33.", name);
    MessageBox(g_hWnd, msg, APP_TITLE, MB_OK | MB_ICONINFORMATION);
    ShowWindow(g_hWnd, SW_MINIMIZE);
}

static void DuplicateSelected(void)
{
    char src[32], dst[32];
    if (!GetSelectedJob(src)) return;
    GetWindowText(g_hNewName, dst, sizeof(dst));
    if (!dst[0]) {
        MessageBox(g_hWnd, "Wpisz nowa nazwe pliku zlecenia.", APP_TITLE,
            MB_OK | MB_ICONEXCLAMATION);
        return;
    }
    if (CopyJobAs(src, dst)) {
        char m[160];
        sprintf(m, "Utworzono nowe zlecenie %s jako kopie %s.\n"
                   "Pierwsza linia i data startu zostaly zaktualizowane.", dst, src);
        MessageBox(g_hWnd, m, APP_TITLE, MB_OK | MB_ICONINFORMATION);
        RefreshJobs();
    }
}

static void DeleteSelected(void)
{
    char name[32], path[128], msg[160];
    if (!GetSelectedJob(name)) return;
    sprintf(msg, "Usunac plik zlecenia %s?", name);
    if (MessageBox(g_hWnd, msg, APP_TITLE,
        MB_YESNO | MB_ICONQUESTION | MB_DEFBUTTON2) != IDYES) return;
    BuildPath(path, name);
    if (remove(path) != 0)
        MessageBox(g_hWnd, "Nie mozna usunac pliku.", APP_TITLE, MB_OK | MB_ICONSTOP);
    RefreshJobs();
}

static LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam)
{
    switch (msg) {
    case WM_CREATE:
        CreateWindow("STATIC", "Zlecenia C:\\Q016FICS", WS_CHILD | WS_VISIBLE,
            12, 10, 250, 18, hwnd, NULL, g_hInst, NULL);
        g_hMode = CreateWindow("STATIC", "Tryb: oczekiwanie na InTouch",
            WS_CHILD | WS_VISIBLE, 285, 10, 310, 18, hwnd, (HMENU)IDC_MODE, g_hInst, NULL);
        g_hList = CreateWindow("LISTBOX", "", WS_CHILD | WS_VISIBLE | WS_BORDER |
            LBS_NOTIFY | WS_VSCROLL, 12, 34, 270, 240, hwnd, (HMENU)IDC_LIST, g_hInst, NULL);

        CreateWindow("BUTTON", "ODSWIEZ", WS_CHILD | WS_VISIBLE,
            300, 38, 135, 28, hwnd, (HMENU)IDC_REFRESH, g_hInst, NULL);
        CreateWindow("BUTTON", "ZALADUJ DO MASZYNY", WS_CHILD | WS_VISIBLE | BS_DEFPUSHBUTTON,
            300, 74, 235, 34, hwnd, (HMENU)IDC_LOAD, g_hInst, NULL);

        CreateWindow("STATIC", "Nowa nazwa DOS 8.3:", WS_CHILD | WS_VISIBLE,
            300, 126, 180, 18, hwnd, NULL, g_hInst, NULL);
        g_hNewName = CreateWindow("EDIT", "", WS_CHILD | WS_VISIBLE | WS_BORDER | ES_AUTOHSCROLL,
            300, 146, 160, 24, hwnd, (HMENU)IDC_NEWNAME, g_hInst, NULL);
        CreateWindow("BUTTON", "NOWE Z ZAZNACZONEGO", WS_CHILD | WS_VISIBLE,
            300, 180, 235, 30, hwnd, (HMENU)IDC_DUP, g_hInst, NULL);
        CreateWindow("BUTTON", "USUN ZLECENIE", WS_CHILD | WS_VISIBLE,
            300, 218, 160, 28, hwnd, (HMENU)IDC_DELETE, g_hInst, NULL);
        CreateWindow("BUTTON", "MINIMALIZUJ", WS_CHILD | WS_VISIBLE,
            300, 252, 160, 28, hwnd, (HMENU)IDC_MINIMIZE, g_hInst, NULL);

        g_hStatus = CreateWindow("STATIC", "DDE: inicjalizacja...",
            WS_CHILD | WS_VISIBLE | SS_LEFT, 12, 292, 570, 20, hwnd, (HMENU)IDC_STATUS, g_hInst, NULL);
        CreateWindow("STATIC",
            "Q016SUP Replacement v0.1 | InTouch pozostaje glownym sterownikiem sekwencji zlecenia",
            WS_CHILD | WS_VISIBLE | SS_LEFT, 12, 316, 570, 18, hwnd, NULL, g_hInst, NULL);

        RefreshJobs();
        SetTimer(hwnd, TIMER_DDE, 1000, NULL);
        return 0;

    case WM_TIMER:
        if (wParam == TIMER_DDE) PollInTouch();
        return 0;

    case WM_COMMAND:
        switch (LOWORD(wParam)) {
        case IDC_REFRESH: RefreshJobs(); break;
        case IDC_LOAD: LoadSelectedJob(); break;
        case IDC_DUP: DuplicateSelected(); break;
        case IDC_DELETE: DeleteSelected(); break;
        case IDC_MINIMIZE: ShowWindow(hwnd, SW_MINIMIZE); break;
        case IDC_LIST:
            if (HIWORD(lParam) == LBN_DBLCLK) LoadSelectedJob();
            break;
        }
        return 0;

    case WM_CLOSE:
        ShowWindow(hwnd, SW_MINIMIZE);
        return 0;

    case WM_DESTROY:
        KillTimer(hwnd, TIMER_DDE);
        DdeDisconnectClient();
        PostQuitMessage(0);
        return 0;
    }
    return DefWindowProc(hwnd, msg, wParam, lParam);
}

int PASCAL WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance,
    LPSTR lpCmdLine, int nCmdShow)
{
    WNDCLASS wc;
    MSG msg;
    (void)lpCmdLine;

    g_hInst = hInstance;
    if (!hPrevInstance) {
        memset(&wc, 0, sizeof(wc));
        wc.style = CS_HREDRAW | CS_VREDRAW;
        wc.lpfnWndProc = WndProc;
        wc.hInstance = hInstance;
        wc.hIcon = LoadIcon(NULL, IDI_APPLICATION);
        wc.hCursor = LoadCursor(NULL, IDC_ARROW);
        wc.hbrBackground = (HBRUSH)(COLOR_WINDOW + 1);
        wc.lpszClassName = APP_CLASS;
        if (!RegisterClass(&wc)) return 0;
    }

    g_hWnd = CreateWindow(APP_CLASS, APP_TITLE,
        WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU | WS_MINIMIZEBOX,
        CW_USEDEFAULT, CW_USEDEFAULT, 610, 385,
        NULL, NULL, hInstance, NULL);
    if (!g_hWnd) return 0;

    ShowWindow(g_hWnd, nCmdShow);
    UpdateWindow(g_hWnd);

    while (GetMessage(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
    return (int)msg.wParam;
}
