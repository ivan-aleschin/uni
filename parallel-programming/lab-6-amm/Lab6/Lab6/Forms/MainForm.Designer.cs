namespace Lab6.Forms
{
    partial class MainForm
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
            this.dataGridViewOriginal = new System.Windows.Forms.DataGridView();
            this.dataGridViewResult = new System.Windows.Forms.DataGridView();
            this.txtMatrixSize = new System.Windows.Forms.TextBox();
            this.txtInfinityValue = new System.Windows.Forms.TextBox();
            this.btnGenerateGraph = new System.Windows.Forms.Button();
            this.btnTransitiveClosure = new System.Windows.Forms.Button();
            this.btnShortestPaths = new System.Windows.Forms.Button();
            this.btnConnectivity = new System.Windows.Forms.Button();
            this.btnLongestPaths = new System.Windows.Forms.Button();
            this.lblStatus = new System.Windows.Forms.Label();
            this.label1 = new System.Windows.Forms.Label();
            this.label2 = new System.Windows.Forms.Label();
            this.label3 = new System.Windows.Forms.Label();
            this.label4 = new System.Windows.Forms.Label();
            
            // 
            // dataGridViewOriginal
            // 
            this.dataGridViewOriginal.Location = new System.Drawing.Point(20, 50);
            this.dataGridViewOriginal.Name = "dataGridViewOriginal";
            this.dataGridViewOriginal.Size = new System.Drawing.Size(350, 300);
            this.dataGridViewOriginal.TabIndex = 0;
            // 
            // dataGridViewResult
            // 
            this.dataGridViewResult.Location = new System.Drawing.Point(400, 50);
            this.dataGridViewResult.Name = "dataGridViewResult";
            this.dataGridViewResult.Size = new System.Drawing.Size(350, 300);
            this.dataGridViewResult.TabIndex = 1;
            // 
            // txtMatrixSize
            // 
            this.txtMatrixSize.Location = new System.Drawing.Point(120, 20);
            this.txtMatrixSize.Name = "txtMatrixSize";
            this.txtMatrixSize.Size = new System.Drawing.Size(50, 23);
            this.txtMatrixSize.TabIndex = 2;
            // 
            // txtInfinityValue
            // 
            this.txtInfinityValue.Location = new System.Drawing.Point(300, 20);
            this.txtInfinityValue.Name = "txtInfinityValue";
            this.txtInfinityValue.Size = new System.Drawing.Size(50, 23);
            this.txtInfinityValue.TabIndex = 3;
            // 
            // btnGenerateGraph
            // 
            this.btnGenerateGraph.Location = new System.Drawing.Point(20, 360);
            this.btnGenerateGraph.Name = "btnGenerateGraph";
            this.btnGenerateGraph.Size = new System.Drawing.Size(120, 30);
            this.btnGenerateGraph.TabIndex = 4;
            this.btnGenerateGraph.Text = "Сгенерировать граф";
            this.btnGenerateGraph.UseVisualStyleBackColor = true;
            this.btnGenerateGraph.Click += new System.EventHandler(this.btnGenerateGraph_Click);
            // 
            // btnTransitiveClosure
            // 
            this.btnTransitiveClosure.Location = new System.Drawing.Point(150, 360);
            this.btnTransitiveClosure.Name = "btnTransitiveClosure";
            this.btnTransitiveClosure.Size = new System.Drawing.Size(120, 30);
            this.btnTransitiveClosure.TabIndex = 5;
            this.btnTransitiveClosure.Text = "Транзитивное замыкание";
            this.btnTransitiveClosure.UseVisualStyleBackColor = true;
            this.btnTransitiveClosure.Click += new System.EventHandler(this.btnTransitiveClosure_Click);
            // 
            // btnShortestPaths
            // 
            this.btnShortestPaths.Location = new System.Drawing.Point(280, 360);
            this.btnShortestPaths.Name = "btnShortestPaths";
            this.btnShortestPaths.Size = new System.Drawing.Size(120, 30);
            this.btnShortestPaths.TabIndex = 6;
            this.btnShortestPaths.Text = "Кратчайшие пути";
            this.btnShortestPaths.UseVisualStyleBackColor = true;
            this.btnShortestPaths.Click += new System.EventHandler(this.btnShortestPaths_Click);
            // 
            // btnConnectivity
            // 
            this.btnConnectivity.Location = new System.Drawing.Point(410, 360);
            this.btnConnectivity.Name = "btnConnectivity";
            this.btnConnectivity.Size = new System.Drawing.Size(120, 30);
            this.btnConnectivity.TabIndex = 7;
            this.btnConnectivity.Text = "Связность графа";
            this.btnConnectivity.Click += new System.EventHandler(this.btnConnectivity_Click);
            // 
            // btnLongestPaths
            // 
            this.btnLongestPaths.Location = new System.Drawing.Point(540, 360);
            this.btnLongestPaths.Name = "btnLongestPaths";
            this.btnLongestPaths.Size = new System.Drawing.Size(120, 30);
            this.btnLongestPaths.TabIndex = 8;
            this.btnLongestPaths.Text = "Длиннейшие пути";
            this.btnLongestPaths.UseVisualStyleBackColor = true;
            this.btnLongestPaths.Click += new System.EventHandler(this.btnLongestPaths_Click);
            // 
            // lblStatus
            // 
            this.lblStatus.AutoSize = true;
            this.lblStatus.Location = new System.Drawing.Point(20, 400);
            this.lblStatus.Name = "lblStatus";
            this.lblStatus.Size = new System.Drawing.Size(82, 15);
            this.lblStatus.TabIndex = 9;
            this.lblStatus.Text = "Готов к работе";
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(20, 23);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(94, 15);
            this.label1.TabIndex = 10;
            this.label1.Text = "Размер матрицы:";
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(200, 23);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(94, 15);
            this.label2.TabIndex = 11;
            this.label2.Text = "Значение ∞ (inf):";
            // 
            // label3
            // 
            this.label3.AutoSize = true;
            this.label3.Location = new System.Drawing.Point(20, 30);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(0, 15);
            this.label3.TabIndex = 12;
            // 
            // label4
            // 
            this.label4.AutoSize = true;
            this.label4.Location = new System.Drawing.Point(400, 30);
            this.label4.Name = "label4";
            this.label4.Size = new System.Drawing.Size(0, 15);
            this.label4.TabIndex = 13;
            // 
            // MainForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(7F, 15F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(784, 441);
            this.Controls.Add(this.label4);
            this.Controls.Add(this.label3);
            this.Controls.Add(this.label2);
            this.Controls.Add(this.label1);
            this.Controls.Add(this.lblStatus);
            this.Controls.Add(this.btnLongestPaths);
            this.Controls.Add(this.btnConnectivity);
            this.Controls.Add(this.btnShortestPaths);
            this.Controls.Add(this.btnTransitiveClosure);
            this.Controls.Add(this.btnGenerateGraph);
            this.Controls.Add(this.txtInfinityValue);
            this.Controls.Add(this.txtMatrixSize);
            this.Controls.Add(this.dataGridViewResult);
            this.Controls.Add(this.dataGridViewOriginal);
            this.Name = "MainForm";
            this.Text = "Lab6 - Абстрактная Матричная Машина и Алгоритм Флойда-Уоршелла";
            ((System.ComponentModel.ISupportInitialize)this.dataGridViewOriginal).EndInit();
            ((System.ComponentModel.ISupportInitialize)this.dataGridViewResult).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.DataGridView dataGridViewOriginal;
        private System.Windows.Forms.DataGridView dataGridViewResult;
        private System.Windows.Forms.TextBox txtMatrixSize;
        private System.Windows.Forms.TextBox txtInfinityValue;
        private System.Windows.Forms.Button btnGenerateGraph;
        private System.Windows.Forms.Button btnTransitiveClosure;
        private System.Windows.Forms.Button btnShortestPaths;
        private System.Windows.Forms.Button btnConnectivity;
        private System.Windows.Forms.Button btnLongestPaths;
        private System.Windows.Forms.Label lblStatus;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.Label label3;
        private System.Windows.Forms.Label label4;
    }
}