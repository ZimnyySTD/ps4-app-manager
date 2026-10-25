#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <dirent.h>
#include <unistd.h>
#include "app_manager.h"

#define PREFS_PATH "/data/ps4_app_manager_prefs.cfg"
#define DEFAULT_BACKUP_DIR "/data/ps4_app_backups"

static void ensure_directory(const char *path) {
    struct stat st = {0};
    if (stat(path, &st) == -1) {
        mkdir(path, 0777);
    }
}

void app_manager_init(AppManagerContext *ctx) {
    if (!ctx) return;
    memset(ctx, 0, sizeof(AppManagerContext));
    ctx->count = 0;
    ctx->selected_index = 0;
    ctx->dark_mode = true;
    ctx->auto_backup = false;
    strncpy(ctx->backup_dir, DEFAULT_BACKUP_DIR, sizeof(ctx->backup_dir) - 1);

    ensure_directory(DEFAULT_BACKUP_DIR);
    app_manager_load_preferences(ctx);
    app_manager_scan_apps(ctx);
}

void app_manager_scan_apps(AppManagerContext *ctx) {
    if (!ctx) return;
    ctx->count = 0;

    const char *search_paths[] = {
        "/user/app",
        "/system/app",
        "/mnt/sandbox/pfsmnt"
    };

    for (size_t p = 0; p < sizeof(search_paths)/sizeof(search_paths[0]); p++) {
        DIR *dir = opendir(search_paths[p]);
        if (!dir) continue;

        struct dirent *entry;
        while ((entry = readdir(dir)) != NULL && ctx->count < MAX_APPS) {
            if (entry->d_name[0] == '.') continue;

            AppInfo *app = &ctx->apps[ctx->count];
            snprintf(app->title_id, sizeof(app->title_id), "%.15s", entry->d_name);
            snprintf(app->name, sizeof(app->name), "App %s", entry->d_name);
            snprintf(app->app_path, sizeof(app->app_path), "%s/%s", search_paths[p], entry->d_name);
            snprintf(app->icon_path, sizeof(app->icon_path), "%s/icon0.png", app->app_path);
            app->category = (p == 1) ? APP_CATEGORY_SYSTEM : APP_CATEGORY_GAME;
            app->is_hidden = false;
            app->custom_icon_set = false;
            app->app_size_bytes = 1024 * 1024 * 50;
            ctx->count++;
        }
        closedir(dir);
    }

    if (ctx->count == 0) {
        AppInfo default_apps[] = {
            {"CUSA00001", "Sample Game Title", "/user/app/CUSA00001/icon0.png", "/user/app/CUSA00001", APP_CATEGORY_GAME, false, false, 1024ULL * 1024 * 1500},
            {"PS4APP000", "PS4 App Manager", "/user/app/PS4APP000/icon0.png", "/user/app/PS4APP000", APP_CATEGORY_HOMEBREW, false, false, 1024ULL * 1024 * 25},
            {"CUSA00002", "Media Player", "/system/app/CUSA00002/icon0.png", "/system/app/CUSA00002", APP_CATEGORY_SYSTEM, false, false, 1024ULL * 1024 * 80}
        };
        for (size_t i = 0; i < sizeof(default_apps)/sizeof(default_apps[0]); i++) {
            ctx->apps[ctx->count++] = default_apps[i];
        }
    }
}

bool app_manager_toggle_hide(AppManagerContext *ctx, size_t index) {
    if (!ctx || index >= ctx->count) return false;

    ctx->apps[index].is_hidden = !ctx->apps[index].is_hidden;
    app_manager_save_preferences(ctx);
    return true;
}

bool app_manager_backup_app(AppManagerContext *ctx, size_t index) {
    if (!ctx || index >= ctx->count) return false;

    AppInfo *app = &ctx->apps[index];
    char target_path[MAX_PATH_LEN];
    snprintf(target_path, sizeof(target_path), "%s/%s.bak", ctx->backup_dir, app->title_id);

    ensure_directory(ctx->backup_dir);
    FILE *f = fopen(target_path, "w");
    if (!f) return false;

    fprintf(f, "TITLE_ID=%s\nNAME=%s\nPATH=%s\nCATEGORY=%d\n", app->title_id, app->name, app->app_path, app->category);
    fclose(f);

    return true;
}

bool app_manager_restore_app(AppManagerContext *ctx, const char *title_id) {
    if (!ctx || !title_id) return false;

    char source_path[MAX_PATH_LEN];
    snprintf(source_path, sizeof(source_path), "%s/%s.bak", ctx->backup_dir, title_id);

    FILE *f = fopen(source_path, "r");
    if (!f) return false;

    fclose(f);
    app_manager_scan_apps(ctx);
    return true;
}

bool app_manager_set_custom_icon(AppManagerContext *ctx, size_t index, const char *new_icon_path) {
    if (!ctx || index >= ctx->count || !new_icon_path) return false;

    strncpy(ctx->apps[index].icon_path, new_icon_path, sizeof(ctx->apps[index].icon_path) - 1);
    ctx->apps[index].custom_icon_set = true;
    app_manager_save_preferences(ctx);
    return true;
}

bool app_manager_save_preferences(const AppManagerContext *ctx) {
    if (!ctx) return false;

    FILE *f = fopen(PREFS_PATH, "w");
    if (!f) return false;

    fprintf(f, "dark_mode=%d\n", ctx->dark_mode ? 1 : 0);
    fprintf(f, "auto_backup=%d\n", ctx->auto_backup ? 1 : 0);
    fprintf(f, "backup_dir=%s\n", ctx->backup_dir);

    for (size_t i = 0; i < ctx->count; i++) {
        fprintf(f, "app:%s:hidden=%d\n", ctx->apps[i].title_id, ctx->apps[i].is_hidden ? 1 : 0);
        if (ctx->apps[i].custom_icon_set) {
            fprintf(f, "app:%s:icon=%s\n", ctx->apps[i].title_id, ctx->apps[i].icon_path);
        }
    }

    fclose(f);
    return true;
}

bool app_manager_load_preferences(AppManagerContext *ctx) {
    if (!ctx) return false;

    FILE *f = fopen(PREFS_PATH, "r");
    if (!f) return false;

    char line[256];
    while (fgets(line, sizeof(line), f)) {
        int val;
        if (sscanf(line, "dark_mode=%d", &val) == 1) {
            ctx->dark_mode = (val != 0);
        } else if (sscanf(line, "auto_backup=%d", &val) == 1) {
            ctx->auto_backup = (val != 0);
        }
    }

    fclose(f);
    return true;
}
