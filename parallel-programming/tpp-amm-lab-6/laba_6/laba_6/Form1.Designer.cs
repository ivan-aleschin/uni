namespace laba_6
{
    partial class Form1
    {
        private System.ComponentModel.IContainer components = null;

        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        private void InitializeComponent()
        {
            this.groupBox1 = new System.Windows.Forms.GroupBox();
            this.btnProfile = new System.Windows.Forms.Button();
            this.btnStart = new System.Windows.Forms.Button();
            this.cmbThreads = new System.Windows.Forms.ComboBox();
            this.label2 = new System.Windows.Forms.Label();
            this.txtMaxNumber = new System.Windows.Forms.TextBox();
            this.label1 = new System.Windows.Forms.Label();
            this.groupBox2 = new System.Windows.Forms.GroupBox();
            this.txtProgress = new System.Windows.Forms.Label();
            this.progressBar = new System.Windows.Forms.ProgressBar();
            this.groupBox3 = new System.Windows.Forms.GroupBox();
            this.txtResults = new System.Windows.Forms.Label();
            this.groupBox4 = new System.Windows.Forms.GroupBox();
            this.txtExamples = new System.Windows.Forms.TextBox();
            this.groupBox5 = new System.Windows.Forms.GroupBox();
            this.txtThreadStats = new System.Windows.Forms.TextBox();
            this.groupBox6 = new System.Windows.Forms.GroupBox();
            this.txtDetails = new System.Windows.Forms.TextBox();
            this.statusStrip1 = new System.Windows.Forms.StatusStrip();
            this.txtStatus = new System.Windows.Forms.ToolStripStatusLabel();
            this.txtMemory = new System.Windows.Forms.ToolStripStatusLabel();
            this.groupBox1.SuspendLayout();
            this.groupBox2.SuspendLayout();
            this.groupBox3.SuspendLayout();
            this.groupBox4.SuspendLayout();
            this.groupBox5.SuspendLayout();
            this.groupBox6.SuspendLayout();
            this.statusStrip1.SuspendLayout();
            this.SuspendLayout();
            // 
            // groupBox1
            // 
            this.groupBox1.Controls.Add(this.btnProfile);
            this.groupBox1.Controls.Add(this.btnStart);
            this.groupBox1.Controls.Add(this.cmbThreads);
            this.groupBox1.Controls.Add(this.label2);
            this.groupBox1.Controls.Add(this.txtMaxNumber);
            this.groupBox1.Controls.Add(this.label1);
            this.groupBox1.Location = new System.Drawing.Point(12, 12);
            this.groupBox1.Name = "groupBox1";
            this.groupBox1.Size = new System.Drawing.Size(760, 70);
            this.groupBox1.TabIndex = 0;
            this.groupBox1.TabStop = false;
            this.groupBox1.Text = "Параметры выполнения";
            // 
            // btnProfile
            // 
            this.btnProfile.BackColor = System.Drawing.Color.LightCyan;
            this.btnProfile.Location = new System.Drawing.Point(550, 25);
            this.btnProfile.Name = "btnProfile";
            this.btnProfile.Size = new System.Drawing.Size(150, 30);
            this.btnProfile.TabIndex = 5;
            this.btnProfile.Text = "Запуск профилирования";
            this.btnProfile.UseVisualStyleBackColor = false;
            this.btnProfile.Click += new System.EventHandler(this.BtnProfile_Click);
            // 
            // btnStart
            // 
            this.btnStart.Location = new System.Drawing.Point(400, 25);
            this.btnStart.Name = "btnStart";
            this.btnStart.Size = new System.Drawing.Size(130, 30);
            this.btnStart.TabIndex = 4;
            this.btnStart.Text = "Запуск вычислений";
            this.btnStart.UseVisualStyleBackColor = true;
            this.btnStart.Click += new System.EventHandler(this.BtnStart_Click);
            // 
            // cmbThreads
            // 
            this.cmbThreads.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.cmbThreads.FormattingEnabled = true;
            this.cmbThreads.Items.AddRange(new object[] {
            "Авто",
            "1",
            "2",
            "4",
            "8"});
            this.cmbThreads.Location = new System.Drawing.Point(280, 28);
            this.cmbThreads.Name = "cmbThreads";
            this.cmbThreads.Size = new System.Drawing.Size(80, 23);
            this.cmbThreads.TabIndex = 3;
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(220, 32);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(54, 15);
            this.label2.TabIndex = 2;
            this.label2.Text = "Потоки:";
            // 
            // txtMaxNumber
            // 
            this.txtMaxNumber.Location = new System.Drawing.Point(130, 28);
            this.txtMaxNumber.Name = "txtMaxNumber";
            this.txtMaxNumber.Size = new System.Drawing.Size(80, 23);
            this.txtMaxNumber.TabIndex = 1;
            this.txtMaxNumber.Text = "100000";
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(20, 32);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(104, 15);
            this.label1.TabIndex = 0;
            this.label1.Text = "N (макс. число):";
            // 
            // groupBox2
            // 
            this.groupBox2.Controls.Add(this.txtProgress);
            this.groupBox2.Controls.Add(this.progressBar);
            this.groupBox2.Location = new System.Drawing.Point(12, 88);
            this.groupBox2.Name = "groupBox2";
            this.groupBox2.Size = new System.Drawing.Size(760, 60);
            this.groupBox2.TabIndex = 1;
            this.groupBox2.TabStop = false;
            this.groupBox2.Text = "Прогресс";
            // 
            // txtProgress
            // 
            this.txtProgress.AutoSize = true;
            this.txtProgress.Location = new System.Drawing.Point(20, 35);
            this.txtProgress.Name = "txtProgress";
            this.txtProgress.Size = new System.Drawing.Size(82, 15);
            this.txtProgress.TabIndex = 1;
            this.txtProgress.Text = "Готов к работе";
            // 
            // progressBar
            // 
            this.progressBar.Location = new System.Drawing.Point(130, 30);
            this.progressBar.Name = "progressBar";
            this.progressBar.Size = new System.Drawing.Size(600, 20);
            this.progressBar.TabIndex = 0;
            // 
            // groupBox3
            // 
            this.groupBox3.Controls.Add(this.txtResults);
            this.groupBox3.Location = new System.Drawing.Point(12, 154);
            this.groupBox3.Name = "groupBox3";
            this.groupBox3.Size = new System.Drawing.Size(760, 50);
            this.groupBox3.TabIndex = 2;
            this.groupBox3.TabStop = false;
            this.groupBox3.Text = "Результаты выполнения";
            // 
            // txtResults
            // 
            this.txtResults.AutoSize = true;
            this.txtResults.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point);
            this.txtResults.Location = new System.Drawing.Point(20, 22);
            this.txtResults.Name = "txtResults";
            this.txtResults.Size = new System.Drawing.Size(91, 15);
            this.txtResults.TabIndex = 0;
            this.txtResults.Text = "Время: - | Обработано: -";
            // 
            // groupBox4
            // 
            this.groupBox4.Controls.Add(this.txtExamples);
            this.groupBox4.Location = new System.Drawing.Point(12, 210);
            this.groupBox4.Name = "groupBox4";
            this.groupBox4.Size = new System.Drawing.Size(370, 150);
            this.groupBox4.TabIndex = 3;
            this.groupBox4.TabStop = false;
            this.groupBox4.Text = "Примеры разложений";
            // 
            // txtExamples
            // 
            this.txtExamples.Location = new System.Drawing.Point(10, 22);
            this.txtExamples.Multiline = true;
            this.txtExamples.Name = "txtExamples";
            this.txtExamples.ReadOnly = true;
            this.txtExamples.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
            this.txtExamples.Size = new System.Drawing.Size(350, 120);
            this.txtExamples.TabIndex = 0;
            // 
            // groupBox5
            // 
            this.groupBox5.Controls.Add(this.txtThreadStats);
            this.groupBox5.Location = new System.Drawing.Point(402, 210);
            this.groupBox5.Name = "groupBox5";
            this.groupBox5.Size = new System.Drawing.Size(370, 150);
            this.groupBox5.TabIndex = 4;
            this.groupBox5.TabStop = false;
            this.groupBox5.Text = "Статистика потоков";
            // 
            // txtThreadStats
            // 
            this.txtThreadStats.Location = new System.Drawing.Point(10, 22);
            this.txtThreadStats.Multiline = true;
            this.txtThreadStats.Name = "txtThreadStats";
            this.txtThreadStats.ReadOnly = true;
            this.txtThreadStats.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
            this.txtThreadStats.Size = new System.Drawing.Size(350, 120);
            this.txtThreadStats.TabIndex = 0;
            // 
            // groupBox6
            // 
            this.groupBox6.Controls.Add(this.txtDetails);
            this.groupBox6.Location = new System.Drawing.Point(12, 370);
            this.groupBox6.Name = "groupBox6";
            this.groupBox6.Size = new System.Drawing.Size(760, 180);
            this.groupBox6.TabIndex = 5;
            this.groupBox6.TabStop = false;
            this.groupBox6.Text = "Детальная информация";
            // 
            // txtDetails
            // 
            this.txtDetails.Font = new System.Drawing.Font("Consolas", 8.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.txtDetails.Location = new System.Drawing.Point(10, 22);
            this.txtDetails.Multiline = true;
            this.txtDetails.Name = "txtDetails";
            this.txtDetails.ReadOnly = true;
            this.txtDetails.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
            this.txtDetails.Size = new System.Drawing.Size(740, 150);
            this.txtDetails.TabIndex = 0;
            // 
            // statusStrip1
            // 
            this.statusStrip1.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.txtStatus,
            this.txtMemory});
            this.statusStrip1.Location = new System.Drawing.Point(0, 559);
            this.statusStrip1.Name = "statusStrip1";
            this.statusStrip1.Size = new System.Drawing.Size(784, 22);
            this.statusStrip1.TabIndex = 6;
            this.statusStrip1.Text = "statusStrip1";
            // 
            // txtStatus
            // 
            this.txtStatus.Name = "txtStatus";
            this.txtStatus.Size = new System.Drawing.Size(39, 17);
            this.txtStatus.Text = "Готов";
            // 
            // txtMemory
            // 
            this.txtMemory.Name = "txtMemory";
            this.txtMemory.Size = new System.Drawing.Size(58, 17);
            this.txtMemory.Text = "Память: -";
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(7F, 15F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(784, 581);
            this.Controls.Add(this.statusStrip1);
            this.Controls.Add(this.groupBox6);
            this.Controls.Add(this.groupBox5);
            this.Controls.Add(this.groupBox4);
            this.Controls.Add(this.groupBox3);
            this.Controls.Add(this.groupBox2);
            this.Controls.Add(this.groupBox1);
            this.Name = "Form1";
            this.Text = "Тестирование производительности - Разложение на множители";
            this.Load += new System.EventHandler(this.Form1_Load);
            this.groupBox1.ResumeLayout(false);
            this.groupBox1.PerformLayout();
            this.groupBox2.ResumeLayout(false);
            this.groupBox2.PerformLayout();
            this.groupBox3.ResumeLayout(false);
            this.groupBox3.PerformLayout();
            this.groupBox4.ResumeLayout(false);
            this.groupBox4.PerformLayout();
            this.groupBox5.ResumeLayout(false);
            this.groupBox5.PerformLayout();
            this.groupBox6.ResumeLayout(false);
            this.groupBox6.PerformLayout();
            this.statusStrip1.ResumeLayout(false);
            this.statusStrip1.PerformLayout();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private GroupBox groupBox1;
        private Button btnProfile;
        private Button btnStart;
        private ComboBox cmbThreads;
        private Label label2;
        private TextBox txtMaxNumber;
        private Label label1;
        private GroupBox groupBox2;
        private Label txtProgress;
        private ProgressBar progressBar;
        private GroupBox groupBox3;
        private Label txtResults;
        private GroupBox groupBox4;
        private TextBox txtExamples;
        private GroupBox groupBox5;
        private TextBox txtThreadStats;
        private GroupBox groupBox6;
        private TextBox txtDetails;
        private StatusStrip statusStrip1;
        private ToolStripStatusLabel txtStatus;
        private ToolStripStatusLabel txtMemory;
    }
}