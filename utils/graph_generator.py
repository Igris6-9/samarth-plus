import matplotlib
matplotlib.use('Agg')  # Server environment (Flask/Acode) ke liye mandatory
import matplotlib.pyplot as plt
import io
import base64

# 👑 DAKASH ENGINE - HYBRID VISUAL ANALYTICS
def generate_progress_graph(dates, scores):
    """
    Cadet ki growth trajectory ka Cinematic Line Graph.
    Optimized for PC (Wide) and Mobile (Flexible).
    """
    try:
        # Theme Calibration
        plt.style.use('dark_background')
        
        # Responsive sizing logic: PC par bada, Mobile par scalable
        fig, ax = plt.subplots(figsize=(10, 5))
        fig.patch.set_facecolor('none') # Background transparent rakho
        ax.set_facecolor('none')

        # Plotting with Neon Glow effect
        ax.plot(dates, scores, marker='o', linestyle='-', color='#00f2ff', 
                linewidth=3, markersize=8, markerfacecolor='#ffffff', 
                markeredgecolor='#00f2ff', label='Neural Path')
        
        # Fill area under curve for 'Aura' effect
        ax.fill_between(dates, scores, color='#00f2ff', alpha=0.1)

        # Spines & Grid Styling
        for spine in ['top', 'right']: ax.spines[spine].set_visible(False)
        ax.spines['left'].set_color('#2d3748')
        ax.spines['bottom'].set_color('#2d3748')
        ax.grid(color='#2d3748', linestyle='--', linewidth=0.5, alpha=0.3)

        # Labels - PC par fonts thode bade
        plt.title('DIVINE RANK TRAJECTORY', family='monospace', fontsize=16, pad=25, color='#00f2ff', fontweight='bold')
        plt.xlabel('MISSIONS', fontsize=10, color='#a0aec0', labelpad=10)
        plt.ylabel('EFFICIENCY %', fontsize=10, color='#a0aec0', labelpad=10)
        plt.ylim(0, 105) # Buffer for text

        # Buffer Export
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', transparent=True, dpi=120)
        buf.seek(0)
        
        img_base64 = base64.b64encode(buf.getvalue()).decode()
        plt.close(fig) # Memory leak bachane ke liye close zaroori hai
        return f"data:image/png;base64,{img_base64}"
    except Exception as e:
        print(f">> [VISUAL ERROR]: {e}")
        return None

def generate_subject_radar(subjects, mastery_levels):
    """
    Subject Mastery Index using Bar Chart.
    """
    try:
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(8, 5))
        fig.patch.set_facecolor('none')
        ax.set_facecolor('none')

        # Divine Color Palette
        colors = ['#00f2ff', '#bc13fe', '#00ff41', '#ff003c', '#ffcc00']
        
        bars = ax.bar(subjects, mastery_levels, color=colors, alpha=0.7, edgecolor='white', linewidth=1, width=0.6)
        
        plt.title('NEURAL SUBJECT MASTERY', family='monospace', fontsize=14, color='#bc13fe', fontweight='bold', pad=20)
        ax.set_ylim(0, 110)
        
        # Grid cleanup
        ax.yaxis.grid(True, color='#2d3748', alpha=0.3)
        ax.xaxis.grid(False)
        for spine in ['top', 'right', 'left']: ax.spines[spine].set_visible(False)

        # Data Labels on Top
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval + 3, f'{yval}%', 
                    ha='center', va='bottom', color='white', fontsize=10, fontweight='bold')

        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', transparent=True, dpi=120)
        buf.seek(0)
        
        img_base64 = base64.b64encode(buf.getvalue()).decode()
        plt.close(fig)
        return f"data:image/png;base64,{img_base64}"
    except Exception as e:
        print(f">> [BAR ERROR]: {e}")
        return None
