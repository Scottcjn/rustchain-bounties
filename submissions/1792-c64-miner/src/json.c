/*
 * RustChain Miner for Commodore 64
 * Minimal JSON builder - no external dependencies
 */

#include <stdio.h>
#include <string.h>
#include <stdint.h>

#include "json.h"

/* ============================================================================
 * JSON Builder
 * ============================================================================ */

void json_init(JsonBuilder* builder, char* buffer, size_t size)
{
    builder->buffer = buffer;
    builder->size = size;
    builder->pos = 0;
    buffer[0] = '\0';
}

int json_begin_object(JsonBuilder* builder)
{
    if (builder->pos >= builder->size - 1) {
        return -1;
    }
    
    builder->buffer[builder->pos++] = '{';
    builder->buffer[builder->pos] = '\0';
    return 0;
}

int json_end_object(JsonBuilder* builder)
{
    if (builder->pos >= builder->size - 1) {
        return -1;
    }
    
    builder->buffer[builder->pos++] = '}';
    builder->buffer[builder->pos] = '\0';
    return 0;
}

int json_begin_array(JsonBuilder* builder)
{
    if (builder->pos >= builder->size - 1) {
        return -1;
    }
    
    builder->buffer[builder->pos++] = '[';
    builder->buffer[builder->pos] = '\0';
    return 0;
}

int json_end_array(JsonBuilder* builder)
{
    if (builder->pos >= builder->size - 1) {
        return -1;
    }
    
    builder->buffer[builder->pos++] = ']';
    builder->buffer[builder->pos] = '\0';
    return 0;
}

int json_add_string(JsonBuilder* builder, const char* key, const char* value)
{
    int written;
    size_t remaining;
    
    remaining = builder->size - builder->pos;
    
    written = snprintf(builder->buffer + builder->pos, remaining,
                       "\"%s\":\"%s\",", key, value);
    
    if (written < 0 || (size_t)written >= remaining) {
        return -1;
    }
    
    builder->pos += written;
    return 0;
}

int json_add_number(JsonBuilder* builder, const char* key, long value)
{
    int written;
    size_t remaining;
    
    remaining = builder->size - builder->pos;
    
    written = snprintf(builder->buffer + builder->pos, remaining,
                       "\"%s\":%ld,", key, value);
    
    if (written < 0 || (size_t)written >= remaining) {
        return -1;
    }
    
    builder->pos += written;
    return 0;
}

int json_add_float(JsonBuilder* builder, const char* key, float value)
{
    int written;
    size_t remaining;
    
    remaining = builder->size - builder->pos;
    
    written = snprintf(builder->buffer + builder->pos, remaining,
                       "\"%s\":%.4f,", key, value);
    
    if (written < 0 || (size_t)written >= remaining) {
        return -1;
    }
    
    builder->pos += written;
    return 0;
}

int json_add_bool(JsonBuilder* builder, const char* key, uint8_t value)
{
    int written;
    size_t remaining;
    
    remaining = builder->size - builder->pos;
    
    written = snprintf(builder->buffer + builder->pos, remaining,
                       "\"%s\":%s,", key, value ? "true" : "false");
    
    if (written < 0 || (size_t)written >= remaining) {
        return -1;
    }
    
    builder->pos += written;
    return 0;
}

/* Remove trailing comma and finalize */
void json_finalize(JsonBuilder* builder)
{
    /* Find last comma and replace with null */
    if (builder->pos > 0 && builder->buffer[builder->pos - 1] == ',') {
        builder->buffer[builder->pos - 1] = '\0';
        builder->pos--;
    }
}

const char* json_get_string(JsonBuilder* builder)
{
    return builder->buffer;
}

size_t json_get_length(JsonBuilder* builder)
{
    return builder->pos;
}

/* ============================================================================
 * Simple JSON Parser (for responses)
 * ============================================================================ */

const char* json_find_string(const char* json, const char* key)
{
    char search[64];
    const char* pos;
    
    snprintf(search, sizeof(search), "\"%s\":", key);
    pos = strstr(json, search);
    
    if (!pos) {
        return NULL;
    }
    
    /* Skip to value */
    pos += strlen(search);
    
    /* Skip whitespace */
    while (*pos == ' ' || *pos == '\t') {
        pos++;
    }
    
    /* Check if string value */
    if (*pos != '"') {
        return NULL;
    }
    
    return pos + 1; /* Skip opening quote */
}

long json_find_number(const char* json, const char* key)
{
    char search[64];
    const char* pos;
    
    snprintf(search, sizeof(search), "\"%s\":", key);
    pos = strstr(json, search);
    
    if (!pos) {
        return 0;
    }
    
    /* Skip to value */
    pos += strlen(search);
    
    /* Skip whitespace */
    while (*pos == ' ' || *pos == '\t') {
        pos++;
    }
    
    /* Parse number */
    return strtol(pos, NULL, 10);
}
