
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def generate_vortex_video(output_path):
    fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
    
    # Simple Vortex Ring / Wake simulation representation
    t = np.linspace(0, 10, 200)
    
    ax.set_xlim(-1, 10)
    ax.set_ylim(-3, 3)
    ax.set_title('Vortex Cylinder: Dynamic Wake Meandering', fontsize=14)
    ax.grid(True, alpha=0.3)
    
    # Rotor
    ax.plot([0, 0], [-1, 1], 'r-', lw=5)
    
    scat = ax.scatter([], [], s=10, c='blue', alpha=0.5)
    
    def animate(i):
        # Create particles representing the wake
        phase = i / 5.0
        x_p = np.linspace(0, 9, 50)
        y_p = 1.0 * np.sin(x_p - phase) + 0.2 * np.random.randn(50)
        y_p2 = -1.0 * np.sin(x_p - phase) + 0.2 * np.random.randn(50)
        
        all_x = np.concatenate([x_p, x_p])
        all_y = np.concatenate([y_p, y_p2])
        
        scat.set_offsets(np.c_[all_x, all_y])
        return scat,

    ani = animation.FuncAnimation(fig, animate, frames=100, interval=50, blit=True)
    writer = animation.FFMpegWriter(fps=20, bitrate=1800)
    ani.save(output_path, writer=writer)
    plt.close(fig)

if __name__ == "__main__":
    generate_vortex_video("vortex_wake.mp4")
