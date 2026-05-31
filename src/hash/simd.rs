#[cfg(target_arch = "x86_64")]
pub fn simd_lookup(key: &[u8], table: &[u8]) -> Option<usize> {
    unsafe {
        let result = std::arch::x86_64::_mm_loadu_si128(key.as_ptr() as *const std::arch::x86_64::__m128i);
        for (i, chunk) in table.chunks(16).enumerate() {
            let chunk_vec = std::arch::x86_64::_mm_loadu_si128(chunk.as_ptr() as *const std::arch::x86_64::__m128i);
            let cmp = std::arch::x86_64::_mm_cmpeq_epi8(result, chunk_vec);
            let mask = std::arch::x86_64::_mm_movemask_epi8(cmp) as u32;
            if mask != 0 { return Some(i * 16 + mask.trailing_zeros() as usize); }
        }
    }
    None
}