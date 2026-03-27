/**
 * Silicon Obituary - Hardware Eulogy Generator
 * Generates a personalized eulogy for retired miners.
 */

function siliconEulogyGenerator(minerName, yearsOperated, minerHash) {
  const eulogyTemplate = `
    The ${yearsOperated} year veteran miner, ${minerName},
    has retired with a final hash of ${minerHash}. 
    Its contributions to the blockchain will not be forgotten.
    Rest in Silicon.
  `;
  return eulogyTemplate.trim();
}

// Example usage:
// console.log(siliconEulogyGenerator('Buckminster-5', 25, '0x1234567890abcdef'));

module.exports = { siliconEulogyGenerator };
