/*
 * RustChain Miner for Commodore 64
 * Minimal JSON builder header
 */

#ifndef JSON_H
#define JSON_H

#include <stdint.h>
#include <stddef.h>

/* JSON builder structure */
typedef struct {
    char* buffer;
    size_t size;
    size_t pos;
} JsonBuilder;

/* Builder functions */
void json_init(JsonBuilder* builder, char* buffer, size_t size);
int json_begin_object(JsonBuilder* builder);
int json_end_object(JsonBuilder* builder);
int json_begin_array(JsonBuilder* builder);
int json_end_array(JsonBuilder* builder);
int json_add_string(JsonBuilder* builder, const char* key, const char* value);
int json_add_number(JsonBuilder* builder, const char* key, long value);
int json_add_float(JsonBuilder* builder, const char* key, float value);
int json_add_bool(JsonBuilder* builder, const char* key, uint8_t value);
void json_finalize(JsonBuilder* builder);
const char* json_get_string(JsonBuilder* builder);
size_t json_get_length(JsonBuilder* builder);

/* Parser functions */
const char* json_find_string(const char* json, const char* key);
long json_find_number(const char* json, const char* key);

#endif /* JSON_H */
