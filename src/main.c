#include <stdio.h>
#include <stdbool.h>
#include <unistd.h>
#include "app_manager.h"
#include "ui.h"

int main(int argc, char *argv[]) {
    printf("Starting PS4 App Manager Native Executable...\n");

    AppManagerContext ctx;
    UIState ui;

    app_manager_init(&ctx);
    ui_init(&ui);

    ui_render(&ctx, &ui);

    if (ctx.count > 0) {
        snprintf(ui.status_message, sizeof(ui.status_message), "Loaded %zu applications.", ctx.count);
        ui_render(&ctx, &ui);
    }

    printf("PS4 App Manager initialized successfully.\n");
    return 0;
}
