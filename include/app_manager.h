#ifndef APP_MANAGER_H
#define APP_MANAGER_H

#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>

#define MAX_TITLE_LEN 128
#define MAX_TITLE_ID_LEN 16
#define MAX_PATH_LEN 512
#define MAX_APPS 256

typedef enum {
    APP_CATEGORY_GAME,
    APP_CATEGORY_HOMEBREW,
    APP_CATEGORY_SYSTEM,
    APP_CATEGORY_UNKNOWN
} AppCategory;

typedef struct {
    char title_id[MAX_TITLE_ID_LEN];
    char name[MAX_TITLE_LEN];
    char icon_path[MAX_PATH_LEN];
    char app_path[MAX_PATH_LEN];
    AppCategory category;
    bool is_hidden;
    bool custom_icon_set;
    uint64_t app_size_bytes;
} AppInfo;

typedef struct {
    AppInfo apps[MAX_APPS];
    size_t count;
    size_t selected_index;
    bool dark_mode;
    bool auto_backup;
    char backup_dir[MAX_PATH_LEN];
} AppManagerContext;

void app_manager_init(AppManagerContext *ctx);
void app_manager_scan_apps(AppManagerContext *ctx);
bool app_manager_toggle_hide(AppManagerContext *ctx, size_t index);
bool app_manager_backup_app(AppManagerContext *ctx, size_t index);
bool app_manager_restore_app(AppManagerContext *ctx, const char *title_id);
bool app_manager_set_custom_icon(AppManagerContext *ctx, size_t index, const char *new_icon_path);
bool app_manager_save_preferences(const AppManagerContext *ctx);
bool app_manager_load_preferences(AppManagerContext *ctx);

#endif // APP_MANAGER_H
