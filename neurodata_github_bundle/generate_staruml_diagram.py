import matplotlib.pyplot as plt
import matplotlib.patches as patches
import json
import os

def draw_staruml_diagram(output_path):
    fig, ax = plt.subplots(figsize=(16, 12), dpi=300)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Grid lines to mimic StarUML Canvas background
    for i in range(0, 17):
        ax.axvline(i, color='#E0E0E0', linestyle='--', linewidth=0.5, alpha=0.6)
    for i in range(0, 13):
        ax.axhline(i, color='#E0E0E0', linestyle='--', linewidth=0.5, alpha=0.6)
        
    # Title Banner (StarUML Diagram Window style)
    ax.text(8, 11.6, "StarUML — ERD (Entity Relationship Diagram) View", 
            fontsize=15, fontweight='bold', ha='center', va='center', color='#003366')
    ax.text(8, 11.2, "Model: NeuroData_DataModel.mdj  |  Notation: Crow's Foot / UML Notation", 
            fontsize=10, fontstyle='italic', ha='center', va='center', color='#424242')

    # StarUML Entity Definitions
    entities = [
        {
            "name": "DATASETS", "x": 0.8, "y": 7.3, "w": 4.0, "h": 3.2,
            "attrs": [
                "«PK» + dataset_id : INTEGER",
                "«UNQ» + table_name : VARCHAR(100)",
                "  + target_database : VARCHAR(50)",
                "  + row_count : BIGINT",
                "  + last_refreshed : TIMESTAMP"
            ]
        },
        {
            "name": "PIPELINES", "x": 6.0, "y": 7.3, "w": 4.0, "h": 3.2,
            "attrs": [
                "«PK» + pipeline_id : INTEGER",
                "«FK» + dataset_id : INTEGER",
                "«UNQ» + pipeline_name : VARCHAR(100)",
                "  + schedule_cron : VARCHAR(50)",
                "  + owner_email : VARCHAR(100)",
                "  + is_active : SMALLINT"
            ]
        },
        {
            "name": "PIPELINE_RUNS", "x": 11.2, "y": 7.3, "w": 4.0, "h": 3.2,
            "attrs": [
                "«PK» + run_id : INTEGER",
                "«FK» + pipeline_id : INTEGER",
                "  + start_time : TIMESTAMP",
                "  + end_time : TIMESTAMP",
                "  + status : VARCHAR(20)",
                "  + records_processed : INTEGER"
            ]
        },
        {
            "name": "QUALITY_RULES", "x": 0.8, "y": 2.2, "w": 4.0, "h": 3.2,
            "attrs": [
                "«PK» + rule_id : INTEGER",
                "«FK» + dataset_id : INTEGER",
                "  + column_name : VARCHAR(100)",
                "  + rule_type : VARCHAR(50)",
                "  + threshold_value : VARCHAR(100)",
                "  + severity : VARCHAR(20)"
            ]
        },
        {
            "name": "RULE_VALIDATIONS", "x": 6.0, "y": 2.2, "w": 4.0, "h": 3.2,
            "attrs": [
                "«PK» + validation_id : INTEGER",
                "«FK» + run_id : INTEGER",
                "«FK» + rule_id : INTEGER",
                "  + passed : SMALLINT",
                "  + failed_row_count : INTEGER",
                "  + validated_at : TIMESTAMP"
            ]
        },
        {
            "name": "ANOMALY_ALERTS", "x": 11.2, "y": 2.2, "w": 4.0, "h": 3.2,
            "attrs": [
                "«PK» + alert_id : INTEGER",
                "«FK» + dataset_id : INTEGER",
                "  + metric_name : VARCHAR(50)",
                "  + expected_value : NUMERIC",
                "  + actual_value : NUMERIC",
                "  + variance_pct : NUMERIC",
                "  + alert_status : VARCHAR(20)"
            ]
        },
        {
            "name": "PIPELINE_LOGS", "x": 6.0, "y": 0.1, "w": 4.0, "h": 1.9,
            "attrs": [
                "«PK» + log_id : INTEGER",
                "«FK» + run_id : INTEGER",
                "  + log_level : VARCHAR(10)",
                "  + message : TEXT",
                "  + created_at : TIMESTAMP"
            ]
        }
    ]

    # Render StarUML Diagram Style Boxes
    for e in entities:
        # Main Outer Rectangle (Yellowish-white header, white body - classic StarUML theme)
        rect = patches.Rectangle((e['x'], e['y']), e['w'], e['h'],
                                 linewidth=1.2, edgecolor='#1C3144', facecolor='#FFFFFF')
        ax.add_patch(rect)
        
        # StarUML Header Box
        header_rect = patches.Rectangle((e['x'], e['y'] + e['h'] - 0.6), e['w'], 0.6,
                                        linewidth=1, edgecolor='#1C3144', facecolor='#FFFDE7')
        ax.add_patch(header_rect)
        
        # Stereotype «entity» and Name
        ax.text(e['x'] + e['w']/2, e['y'] + e['h'] - 0.22, "«entity»",
                fontsize=8, fontstyle='italic', color='#616161', ha='center', va='center')
        ax.text(e['x'] + e['w']/2, e['y'] + e['h'] - 0.44, e['name'],
                fontsize=10, fontweight='bold', color='#1C3144', ha='center', va='center')
        
        # Horizontal Separator Line
        ax.plot([e['x'], e['x'] + e['w']], [e['y'] + e['h'] - 0.6, e['y'] + e['h'] - 0.6],
                color='#1C3144', linewidth=1)
        
        # Attribute items
        y_text = e['y'] + e['h'] - 0.85
        for attr in e['attrs']:
            if "«PK»" in attr:
                color = '#B71C1C'
                weight = 'bold'
            elif "«FK»" in attr:
                color = '#0D47A1'
                weight = 'bold'
            else:
                color = '#212121'
                weight = 'normal'
            ax.text(e['x'] + 0.15, y_text, attr, fontsize=8, fontweight=weight, color=color, ha='left', va='center')
            y_text -= 0.35

    # Connector Drawing Helper (StarUML Association Style with Multiplicity '1' and '0..*')
    def draw_staruml_association(x1, y1, x2, y2, role_name, mult1="1", mult2="0..*"):
        ax.plot([x1, x2], [y1, y2], color='#1C3144', lw=1.3, linestyle='-')
        mid_x, mid_y = (x1 + x2)/2, (y1 + y2)/2
        ax.text(mid_x, mid_y + 0.12, f"«relate»\n{role_name}", fontsize=7.5, fontstyle='italic', ha='center', va='center',
                bbox=dict(boxstyle="square,pad=0.15", facecolor='#F5F5F5', edgecolor='#B0BEC5', alpha=0.9))
        ax.text(x1 + (x2-x1)*0.12, y1 + (y2-y1)*0.12 + 0.15, mult1, fontsize=9, fontweight='bold', color='#003366')
        ax.text(x2 - (x2-x1)*0.12, y2 - (y2-y1)*0.12 + 0.15, mult2, fontsize=9, fontweight='bold', color='#003366')

    # StarUML Model Relationships
    draw_staruml_association(4.8, 8.9, 6.0, 8.9, "ingested_by", "1", "0..*")
    draw_staruml_association(10.0, 8.9, 11.2, 8.9, "executes", "1", "0..*")
    draw_staruml_association(2.8, 7.3, 2.8, 5.4, "has_rules", "1", "0..*")
    draw_staruml_association(12.5, 7.3, 8.5, 5.4, "generates", "1", "0..*")
    draw_staruml_association(4.8, 3.8, 6.0, 3.8, "evaluates", "1", "0..*")
    draw_staruml_association(4.2, 7.3, 11.2, 4.5, "triggers_alert", "1", "0..*")
    draw_staruml_association(13.2, 7.3, 8.5, 2.0, "records_logs", "1", "0..*")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"StarUML diagram image saved at {output_path}")

def generate_staruml_mdj(mdj_path):
    """Generates a valid StarUML .mdj project file."""
    mdj_content = {
        "_type": "Project",
        "_id": "AAAAAAFF+h6SjaM2Hec=",
        "name": "NeuroData_DataModel",
        "ownedElements": [
            {
                "_type": "ERDPackage",
                "_id": "AAAAAAFF+REB19544nM=",
                "_parent": {"$ref": "AAAAAAFF+h6SjaM2Hec="},
                "name": "Data Model",
                "ownedElements": [
                    {
                        "_type": "ERDDataModel",
                        "_id": "AAAAAAGX1234567890A=",
                        "name": "NeuroData ERD",
                        "ownedElements": [
                            {"_type": "ERDEntity", "_id": "E_DATASETS", "name": "DATASETS"},
                            {"_type": "ERDEntity", "_id": "E_PIPELINES", "name": "PIPELINES"},
                            {"_type": "ERDEntity", "_id": "E_PIPELINE_RUNS", "name": "PIPELINE_RUNS"},
                            {"_type": "ERDEntity", "_id": "E_QUALITY_RULES", "name": "QUALITY_RULES"},
                            {"_type": "ERDEntity", "_id": "E_RULE_VALIDATIONS", "name": "RULE_VALIDATIONS"},
                            {"_type": "ERDEntity", "_id": "E_ANOMALY_ALERTS", "name": "ANOMALY_ALERTS"},
                            {"_type": "ERDEntity", "_id": "E_PIPELINE_LOGS", "name": "PIPELINE_LOGS"}
                        ]
                    }
                ]
            }
        ]
    }
    with open(mdj_path, 'w') as f:
        json.dump(mdj_content, f, indent=2)
    print(f"StarUML project file saved at {mdj_path}")

if __name__ == "__main__":
    png_file = os.path.join(os.path.dirname(__file__), "staruml_er_diagram.png")
    mdj_file = os.path.join(os.path.dirname(__file__), "neurodata_staruml.mdj")
    draw_staruml_diagram(png_file)
    generate_staruml_mdj(mdj_file)
