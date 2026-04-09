
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def generate_bem_video(output_path):
    fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
    
    # Streamtube visualization
    x = np.linspace(-2, 5, 100)
    def r(x_val, a):
        # 简化版流管半径公式
        if x_val < 0: return 1.0
        return 1.0 + a * (1 - np.exp(-x_val))
    
    ax.set_xlim(-2, 5)
    ax.set_ylim(-2, 2)
    ax.set_aspect('equal')
    ax.set_title('BEM Theory: Axial Induction & Streamtube Expansion', fontsize=14)
    ax.grid(True, alpha=0.3)
    
    line_up, = ax.plot([], [], 'b-', lw=2)
    line_down, = ax.plot([], [], 'b-', lw=2)
    rotor = ax.axvline(0, color='red', lw=3, label='Rotor Plane')
    
    def animate(i):
        a = 0.1 + 0.2 * (1 + np.sin(i / 10.0)) / 2.0 # Induction factor 0.1 to 0.3
        y = np.array([r(xv, a) for xv in x])
        line_up.set_data(x, y)
        line_down.set_data(x, -y)
        return line_up, line_down

    ani = animation.FuncAnimation(fig, animate, frames=100, interval=50, blit=True)
    writer = animation.FFMpegWriter(fps=20, bitrate=1800)
    ani.save(output_path, writer=writer)
    plt.close(fig)

if __name__ == "__main__":
    generate_bem_video("bem_theory.mp4")
