/*
 * rapl-read: setuid helper to read Intel RAPL energy counters.
 * Outputs one µJ value per line for each domain, then exits.
 *
 * このファイルはソース管理用のコピーです。
 * コンパイル済みバイナリは /usr/local/bin/rapl-read に setuid root で配置する必要があります。
 * バージョン管理外のため、変更後は以下の手順で再インストールしてください:
 *
 *   gcc -O2 -o rapl-read rapl-read.c
 *   sudo install -o root -g root -m 4755 rapl-read /usr/local/bin/rapl-read
 */
#include <stdio.h>
#include <stdlib.h>

/* Domains to read — order is preserved in output */
static const char *const PATHS[] = {
    "/sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj",                    /* package */
    "/sys/class/powercap/intel-rapl/intel-rapl:0/intel-rapl:0:0/energy_uj",     /* core    */
    "/sys/class/powercap/intel-rapl/intel-rapl:0/intel-rapl:0:1/energy_uj",     /* uncore  */
    NULL
};

int main(void) {
    for (int i = 0; PATHS[i]; i++) {
        FILE *f = fopen(PATHS[i], "r");
        if (!f) {
            perror(PATHS[i]);
            return 1;
        }
        unsigned long long uj;
        if (fscanf(f, "%llu", &uj) != 1) {
            fprintf(stderr, "parse error: %s\n", PATHS[i]);
            fclose(f);
            return 1;
        }
        fclose(f);
        printf("%llu\n", uj);
    }
    return 0;
}
