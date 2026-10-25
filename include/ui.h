#ifndef UI_H
#define UI_H

#include "app_manager.h"

typedef enum {
    VIEW_APP_LIST,
    VIEW_APP_DETAILS,
    VIEW_BACKUP_RECOVERY,
    VIEW_SETTINGS
} UIView;

typedef struct {
    UIView current_view;
    char status_message[256];
} UIState;

void ui_init(UIState *state);
void ui_render(const AppManagerContext *ctx, const UIState *state);
void ui_handle_input(AppManagerContext *ctx, UIState *state, int button_code);

#endif // UI_H
