partial class Lab6Form
{
    private System.ComponentModel.IContainer components = null;
    private DataGridView dataGridView1;
    private DataGridView dataGridView2;
    private TextBox txtSize;
    private Button btnGenerateGraph;
    private Button btnTransitiveClosure;
    private Button btnShortestPaths;
    private Button btnConnectivity;
    private Label lblResult;

    protected override void Dispose(bool disposing)
    {
        if (disposing && (components != null))
        {
            components.Dispose();
        }
        base.Dispose(disposing);
    }

    private void InitializeComponent()
    {
        this.dataGridView1 = new DataGridView();
        this.dataGridView2 = new DataGridView();
        this.txtSize = new TextBox();
        this.btnGenerateGraph = new Button();
        this.btnTransitiveClosure = new Button();
        this.btnShortestPaths = new Button();
        this.btnConnectivity = new Button();
        this.lblResult = new Label();
        
        // Настройка контролов
        // ... (аналогично предыдущим формам)
        
        this.Text = "Lab6 - Абстрактная Матричная Машина и Флойд-Уоршелл";
    }
}