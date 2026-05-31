pub struct ZeroCopyBuf<T: ?Sized> {
    ptr: *const T,
    len: usize,
}

impl<T: ?Sized> ZeroCopyBuf<T> {
    pub unsafe fn from_raw(ptr: *const u8, len: usize) -> Self { Self { ptr: ptr as *const T, len } }
    pub fn as_ref(&self) -> &T { unsafe { &*self.ptr } }
}