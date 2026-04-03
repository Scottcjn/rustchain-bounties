import { posterOnExecuted, postActivity, postDiscordMessage } from '../poster';
import fetch from 'node-fetch';

jest.mock('node-fetch', () => jest.fn());
const mockedFetch = fetch as unknown as jest.Mock;

describe('poster', () => {
  beforeEach(() => mockedFetch.mockReset());

  it('posts activity and discord message', async () => {
    mockedFetch.mockResolvedValue({ ok: true });
    const trade = { signature: 'sig1', from: 'A', to: 'B', amount: 1000 } as any;
    await posterOnExecuted(trade, { tx: 'tx1', cluster: 'devnet' });
    expect(mockedFetch).toHaveBeenCalled();
  });
});
