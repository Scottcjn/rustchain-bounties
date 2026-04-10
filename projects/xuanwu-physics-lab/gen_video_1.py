
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os

def generate_transonic_video(output_path):
    # Setup the figure
    fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
    plt.subplots_adjust(bottom=0.2)
    
    # Physics constants (approximate for demo)
    span = np.linspace(0, 140, 100) # 140m blade
    base_wind = 22 # m/s
    omega = 0.8 # rad/s (~7.6 rpm)
    
    line, = ax.plot([], [], 'b-', lw=2, label='Normal Operation')
    safe_line, = ax.plot([], [], 'r--', lw=2, label='Transonic Safe Mode (TSM)')
    point, = ax.plot([], [], 'ko')
    
    ax.set_xlim(0, 140)
    ax.set_ylim(0, 1.2)
    ax.axhline(0.8, color='gray', linestyle=':', label='Transonic Onset (M=0.8)')
    ax.set_xlabel('Blade Span (m)', fontsize=12)
    ax.set_ylabel('Local Mach Number ($M$)', fontsize=12)
    ax.set_title('Xuanwu Physics: Transonic Safe Mode (IEA 22MW)', fontsize=14)
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)

    # Animation data
    def animate(i):
        # Add some "unsteadiness" (gusts)
        gust = 2 * np.sin(i / 10.0)
        v_rel = np.sqrt((base_wind + gust)**2 + (omega * span)**2)
        mach = v_rel / 340.0
        
        line.set_data(span, mach)
        
        # TSM Logic: Cap speed at Mach 0.85
        tsm_mach = np.where(mach > 0.85, 0.85 + 0.05 * np.sin(i/5.0), mach)
        safe_line.set_data(span, tsm_mach)
        
        return line, safe_line

    ani = animation.FuncAnimation(fig, animate, frames=100, interval=50, blit=True)
    
    # Save using ffmpeg
    writer = animation.FFMpegWriter(fps=20, metadata=dict(artist='Xuanwu Bot'), bitrate=1800)
    ani.save(output_path, writer=writer)
    plt.close(fig)

if __name__ == "__main__":
    output = "transonic_safety.mp4"
    print(f"Generating video: {output}...")
    generate_transonic_video(output)
    print("Done.")
