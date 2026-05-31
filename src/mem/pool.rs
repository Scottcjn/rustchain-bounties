pub struct MemoryPool<T> {
    blocks: Vec<Vec<T>>,
    block_size: usize,
}

impl<T: Default + Copy> MemoryPool<T> {
    pub fn new(block_size: usize) -> Self { Self { blocks: vec![vec![T::default(); block_size]], block_size } }
    pub fn alloc(&mut self, val: T) -> usize {
        for (i, block) in self.blocks.iter_mut().enumerate() {
            for (j, slot) in block.iter_mut().enumerate() {
                if *slot == T::default() { *slot = val; return i * self.block_size + j; }
            }
        }
        let idx = self.blocks.len();
        self.blocks.push(vec![T::default(); self.block_size]);
        self.blocks[idx][0] = val;
        idx * self.block_size
    }
}