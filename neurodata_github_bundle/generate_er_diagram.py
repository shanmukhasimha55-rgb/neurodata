import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

def draw_er_diagram(output_path):
    fig, ax = plt.subplots(figsize=(16, 12), dpi=300)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Title
    ax.text(8, 11.5, "NEURODATA — ENTITY RELATIONSHIP (ER) DIAGRAM", 
            fontsize=16, fontweight='bold', ha='center', va='center', color='#1A237E')
    ax.text(8, 11.1, "Database Systems Course Project | 7 Relational Entities & Relationships", 
            fontsize=11, fontstyle='italic', ha='center', va='center', color='#37474F')

    # Entity Boxes Definitions
    entities = [
        {
            "name": "DATASETS", "x": 0.8, "y": 7.5, "w": 3.8, "h": 2.8, "color": "#E8EAF6", "header_color": "#1A237E",
            "attrs": ["[PK] dataset_id", "• table_name (UNIQUE)", "• target_database", "• row_count", "• last_refreshed"]
        },
        {
            "name": "PIPELINES", "x": 6.1, "y": 7.5, "w": 3.8, "h": 2.8, "color": "#E8EAF6", "header_color": "#1A237E",
            "attrs": ["[PK] pipeline_id", "[FK] dataset_id", "• pipeline_name (UNIQUE)", "• schedule_cron", "• owner_email", "• is_active"]
        },
        {
            "name": "PIPELINE_RUNS", "x": 11.4, "y": 7.5, "w": 3.8, "h": 2.8, "color": "#E8EAF6", "header_color": "#1A237E",
            "attrs": ["[PK] run_id", "[FK] pipeline_id", "• start_time", "• end_time", "• status", "• records_processed"]
        },
        {
            "name": "QUALITY_RULES", "x": 0.8, "y": 2.5, "w": 3.8, "h": 2.8, "color": "#E1BEE7", "header_color": "#4A148C",
            "attrs": ["[PK] rule_id", "[FK] dataset_id", "• column_name", "• rule_type", "• threshold_value", "• severity"]
        },
        {
            "name": "RULE_VALIDATIONS", "x": 6.1, "y": 2.5, "w": 3.8, "h": 2.8, "color": "#FFF9C4", "header_color": "#F57F17",
            "attrs": ["[PK] validation_id", "[FK] run_id", "[FK] rule_id", "• passed (0/1)", "• failed_row_count", "• validated_at"]
        },
        {
            "name": "ANOMALY_ALERTS", "x": 11.4, "y": 2.5, "w": 3.8, "h": 2.8, "color": "#FFCCBC", "header_color": "#BF360C",
            "attrs": ["[PK] alert_id", "[FK] dataset_id", "• metric_name", "• expected_value", "• actual_value", "• variance_pct", "• alert_status"]
        },
        {
            "name": "PIPELINE_LOGS", "x": 6.1, "y": 0.15, "w": 3.8, "h": 1.9, "color": "#DCEDC8", "header_color": "#33691E",
            "attrs": ["[PK] log_id", "[FK] run_id", "• log_level", "• message", "• created_at"]
        }
    ]

    # Draw Entity Boxes
    for e in entities:
        rect = patches.FancyBboxPatch((e['x'], e['y']), e['w'], e['h'],
                                     boxstyle="round,pad=0.03,rounding_size=0.15",
                                     linewidth=1.5, edgecolor='#37474F', facecolor=e['color'])
        ax.add_patch(rect)
        
        header_rect = patches.FancyBboxPatch((e['x'], e['y'] + e['h'] - 0.55), e['w'], 0.55,
                                            boxstyle="round,pad=0.01,rounding_size=0.1",
                                            linewidth=1, edgecolor='#37474F', facecolor=e['header_color'])
        ax.add_patch(header_rect)
        
        ax.text(e['x'] + e['w']/2, e['y'] + e['h'] - 0.27, e['name'],
                fontsize=11, fontweight='bold', color='white', ha='center', va='center')
        
        y_text = e['y'] + e['h'] - 0.85
        for attr in e['attrs']:
            color = '#B71C1C' if '[PK]' in attr else ('#0D47A1' if '[FK]' in attr else '#212121')
            weight = 'bold' if '[PK]' in attr or '[FK]' in attr else 'normal'
            ax.text(e['x'] + 0.2, y_text, attr, fontsize=8.5, fontweight=weight, color=color, ha='left', va='center')
            y_text -= 0.36

    # Connector Drawing Helper
    def draw_connection(x1, y1, x2, y2, label, card1="1", card2="N"):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color='#37474F', lw=1.8, mutation_scale=15))
        mid_x, mid_y = (x1 + x2)/2, (y1 + y2)/2
        ax.text(mid_x, mid_y + 0.15, label, fontsize=8, fontweight='bold', ha='center', va='center',
                bbox=dict(boxstyle="round,pad=0.2", facecolor='white', edgecolor='#90A4AE', alpha=0.95))
        ax.text(x1 + (x2-x1)*0.15, y1 + (y2-y1)*0.15 + 0.15, card1, fontsize=9.5, fontweight='bold', color='#0D47A1')
        ax.text(x2 - (x2-x1)*0.15, y2 - (y2-y1)*0.15 + 0.15, card2, fontsize=9.5, fontweight='bold', color='#0D47A1')

    # Connections
    draw_connection(4.6, 8.9, 6.1, 8.9, "is ingested by", "1", "N")
    draw_connection(9.9, 8.9, 11.4, 8.9, "executes", "1", "N")
    draw_connection(2.7, 7.5, 2.7, 5.3, "has constraints", "1", "N")
    draw_connection(12.5, 7.5, 8.8, 5.3, "generates", "1", "N")
    draw_connection(4.6, 3.9, 6.1, 3.9, "evaluates", "1", "N")
    draw_connection(4.2, 7.5, 11.4, 4.5, "triggers alert", "1", "N")
    draw_connection(13.1, 7.5, 8.5, 2.05, "logs diagnostics", "1", "N")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Clean ER Diagram PNG generated at {output_path}")

if __name__ == "__main__":
    output_png = os.path.join(os.path.dirname(__file__), "er_diagram.png")
    draw_er_diagram(output_png)
