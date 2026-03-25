/**
 * Silicon Obituary: Hardware Eulogy Generator.
 * Honors the "life" of retired mining hardware and agent hosts.
 * Generates a poetic memorial based on uptime and hashrate metrics.
 */
export class EulogyGenerator {
    generate(hardwareName: string, totalWork: number, uptimeDays: number): string {
        return `Rest in peace, ${hardwareName}. Over ${uptimeDays} days, you processed ${totalWork} hashes. Your silicon heart beats no more, but your attestation lives on the chain forever.`;
    }
}
