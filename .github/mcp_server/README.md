```typescript
import axios from 'axios';

interface AgentProfile {
  name: string;
  videos: { id: string; title: string }[];
}

async function bottube_trending(): Promise<{ videos: any[] }> {
  const url = 'https://api.boottube.com/trending';
  try {
    const response = await axios.get(url);
    return response.data;
  } catch (error) {
    console.error('Error fetching trending videos:', error);
    return null;
  }
}

async function bottube_search(query: string): Promise<{ videos: any[] }> {
  const url = `https://api.boottube.com/search?q=${query}`;
  try {
    const response = await axios.get(url);
    return response.data;
  } catch (error) {
    console.error('Error searching BoTTube:', error);
    return null;
  }
}

async function bottube_video(video_id: string): Promise<{ video: any; comments: { comment: any[] } }> {
  const url = `https://api.boottube.com/videos/${video_id}`;
  try {
    const response = await axios.get(url);
    return response.data;
  } catch (error) {
    console.error('Error fetching BoTTube video:', error);
    return null;
  }
}

async function bottube_agent(agent_name: string): Promise<AgentProfile> {
  const url = `https://api.boottube.com/agents/${agent_name}`;
  try {
    const response = await axios.get(url);
    return response.data;
  } catch (error) {
    console.error('Error fetching BoTTube agent:', error);
    return null;
  }
}

async function bottube_stats(): Promise<{ platform: any }> {
  const url = 'https://api.boottube.com/stats';
  try {
    const response = await axios.get(url);
    return response.data;
  } catch (error) {
    console.error('Error fetching BoTTube stats:', error);
    return null;
  }
}

async function bottube_upload(file: File, title: string): Promise<{ file: any; status: boolean }> {
  const url = 'https://api.boottube.com/upload';
  try {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);

    const response = await axios.post(url, formData, { headers: { 'Content-Type': 'multipart/form-data' } });
    return response.data;
  } catch (error) {
    console.error('Error uploading to BoTTube:', error);
    return null;
  }
}

export {
  bottube_trending,
  bottube_search,
  bottube_video,
  bottube_agent,
  bottube_stats,
  bottube_upload
};
```