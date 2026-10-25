#include <stdio.h>
#include <string.h>
#include "ui.h"

void ui_init(UIState *state) {
    if (!state) return;
    state->current_view = VIEW_APP_LIST;
    snprintf(state->status_message, sizeof(state->status_message), "Welcome to PS4 App Manager");
}

void ui_render(const AppManagerContext *ctx, const UIState *state) {
    if (!ctx || !state) return;

    printf("\n=======================================================\n");
    printf("              PS4 APP MANAGER (GoldHEN)                \n");
    printf("=======================================================\n");
    printf("Status: %s\n", state->status_message);
    printf("Total Apps: %zu | Selected: %zu\n", ctx->count, ctx->selected_index + 1);
    printf("-------------------------------------------------------\n");

    switch (state->current_view) {
        case VIEW_APP_LIST:
            printf("[VIEW: APPLICATION BROWSER]\n");
            for (size_t i = 0; i < ctx->count; i++) {
                const AppInfo *app = &ctx->apps[i];
                printf(" %s %c [%s] %-20s (Size: %llu MB) %s\n",
                    (i == ctx->selected_index) ? "->" : "  ",
                    app->is_hidden ? 'H' : 'V',
                    app->title_id,
                    app->name,
                    (unsigned long long)(app->app_size_bytes / (1024 * 1024)),
                    app->custom_icon_set ? "[Custom Icon]" : "");
            }
            printf("\nControls: [D-Pad Up/Down] Select | [X] Details | [Square] Toggle Hide | [Triangle] Settings\n");
            break;

        case VIEW_APP_DETAILS:
            if (ctx->count > 0 && ctx->selected_index < ctx->count) {
                const AppInfo *app = &ctx->apps[ctx->selected_index];
                printf("[VIEW: APP DETAILS - %s]\n", app->name);
                printf("  Title ID    : %s\n", app->title_id);
                printf("  App Path    : %s\n", app->app_path);
                printf("  Icon Path   : %s\n", app->icon_path);
                printf("  Hidden State: %s\n", app->is_hidden ? "Hidden" : "Visible");
                printf("  Size        : %llu MB\n", (unsigned long long)(app->app_size_bytes / (1024 * 1024)));
            }
            printf("\nControls: [Circle] Back | [Triangle] Backup App | [L1] Set Custom Icon\n");
            break;

        case VIEW_BACKUP_RECOVERY:
            printf("[VIEW: BACKUP & RECOVERY MANAGER]\n");
            printf("  Backup Location: %s\n", ctx->backup_dir);
            printf("  Auto Backup    : %s\n", ctx->auto_backup ? "Enabled" : "Disabled");
            printf("\nControls: [Circle] Back | [X] Perform Full Backup\n");
            break;

        case VIEW_SETTINGS:
            printf("[VIEW: PREFERENCES & SETTINGS]\n");
            printf("  1. Dark Mode    : %s\n", ctx->dark_mode ? "Enabled" : "Disabled");
            printf("  2. Auto Backup  : %s\n", ctx->auto_backup ? "Enabled" : "Disabled");
            printf("  3. Target Dir   : %s\n", ctx->backup_dir);
            printf("\nControls: [Circle] Back\n");
            break;
    }
    printf("=======================================================\n\n");
}

void ui_handle_input(AppManagerContext *ctx, UIState *state, int button_code) {
    if (!ctx || !state) return;

    enum { UP = 1, DOWN = 2, CROSS = 3, CIRCLE = 4, SQUARE = 5, TRIANGLE = 6 };

    switch (state->current_view) {
        case VIEW_APP_LIST:
            if (button_code == UP && ctx->selected_index > 0) {
                ctx->selected_index--;
            } else if (button_code == DOWN && ctx->selected_index + 1 < ctx->count) {
                ctx->selected_index++;
            } else if (button_code == CROSS) {
                state->current_view = VIEW_APP_DETAILS;
            } else if (button_code == SQUARE) {
                app_manager_toggle_hide(ctx, ctx->selected_index);
                snprintf(state->status_message, sizeof(state->status_message), "Toggled visibility for app");
            } else if (button_code == TRIANGLE) {
                state->current_view = VIEW_SETTINGS;
            }
            break;

        case VIEW_APP_DETAILS:
            if (button_code == CIRCLE) {
                state->current_view = VIEW_APP_LIST;
            } else if (button_code == TRIANGLE) {
                if (app_manager_backup_app(ctx, ctx->selected_index)) {
                    snprintf(state->status_message, sizeof(state->status_message), "Successfully backed up app!");
                } else {
                    snprintf(state->status_message, sizeof(state->status_message), "Failed to back up app.");
                }
            }
            break;

        case VIEW_BACKUP_RECOVERY:
        case VIEW_SETTINGS:
            if (button_code == CIRCLE) {
                state->current_view = VIEW_APP_LIST;
            }
            break;
    }
}
