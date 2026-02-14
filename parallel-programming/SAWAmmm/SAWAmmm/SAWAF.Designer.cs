namespace SAWA
{
    partial class SAWAF
    {
        /// <summary>
        /// Обязательная переменная конструктора.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Освободить все используемые ресурсы.
        /// </summary>
        /// <param name="disposing">истинно, если управляемый ресурс должен быть удален; иначе ложно.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Код, автоматически созданный конструктором форм Windows

        /// <summary>
        /// Требуемый метод для поддержки конструктора — не изменяйте 
        /// содержимое этого метода с помощью редактора кода.
        /// </summary>
        private void InitializeComponent()
        {
            dgArrs = new DataGridView();
            ColA = new DataGridViewTextBoxColumn();
            ColB = new DataGridViewTextBoxColumn();
            ColC = new DataGridViewTextBoxColumn();
            lblB = new Label();
            lblN = new Label();
            lbl_p = new Label();
            tbB = new TextBox();
            tbN = new TextBox();
            tb_p = new TextBox();
            btnCreate = new Button();
            btnShowAB = new Button();
            btnShowC = new Button();
            lblTime = new Label();
            btnSeq = new Button();
            btnPar = new Button();
            button1 = new Button();
            button2 = new Button();
            ((System.ComponentModel.ISupportInitialize)dgArrs).BeginInit();
            SuspendLayout();
            // 
            // dgArrs
            // 
            dgArrs.ColumnHeadersHeightSizeMode = DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            dgArrs.Columns.AddRange(new DataGridViewColumn[] { ColA, ColB, ColC });
            dgArrs.Location = new Point(12, 15);
            dgArrs.Margin = new Padding(3, 2, 3, 2);
            dgArrs.Name = "dgArrs";
            dgArrs.RowHeadersWidth = 51;
            dgArrs.RowTemplate.Height = 24;
            dgArrs.Size = new Size(469, 561);
            dgArrs.TabIndex = 0;
            dgArrs.CellContentClick += dgArrs_CellContentClick;
            // 
            // ColA
            // 
            ColA.HeaderText = "A";
            ColA.MinimumWidth = 6;
            ColA.Name = "ColA";
            ColA.Width = 125;
            // 
            // ColB
            // 
            ColB.HeaderText = "B";
            ColB.MinimumWidth = 6;
            ColB.Name = "ColB";
            ColB.Width = 125;
            // 
            // ColC
            // 
            ColC.HeaderText = "C";
            ColC.MinimumWidth = 6;
            ColC.Name = "ColC";
            ColC.Width = 125;
            // 
            // lblB
            // 
            lblB.AutoSize = true;
            lblB.Location = new Point(528, 61);
            lblB.Name = "lblB";
            lblB.Size = new Size(18, 20);
            lblB.TabIndex = 1;
            lblB.Text = "B";
            // 
            // lblN
            // 
            lblN.AutoSize = true;
            lblN.Location = new Point(527, 105);
            lblN.Name = "lblN";
            lblN.Size = new Size(20, 20);
            lblN.TabIndex = 2;
            lblN.Text = "N";
            // 
            // lbl_p
            // 
            lbl_p.AutoSize = true;
            lbl_p.Location = new Point(529, 155);
            lbl_p.Name = "lbl_p";
            lbl_p.Size = new Size(18, 20);
            lbl_p.TabIndex = 3;
            lbl_p.Text = "p";
            // 
            // tbB
            // 
            tbB.Location = new Point(584, 60);
            tbB.Margin = new Padding(3, 2, 3, 2);
            tbB.Name = "tbB";
            tbB.Size = new Size(120, 27);
            tbB.TabIndex = 4;
            // 
            // tbN
            // 
            tbN.Location = new Point(584, 105);
            tbN.Margin = new Padding(3, 2, 3, 2);
            tbN.Name = "tbN";
            tbN.Size = new Size(119, 27);
            tbN.TabIndex = 5;
            // 
            // tb_p
            // 
            tb_p.Location = new Point(585, 149);
            tb_p.Margin = new Padding(3, 2, 3, 2);
            tb_p.Name = "tb_p";
            tb_p.Size = new Size(119, 27);
            tb_p.TabIndex = 6;
            // 
            // btnCreate
            // 
            btnCreate.Location = new Point(532, 195);
            btnCreate.Margin = new Padding(3, 2, 3, 2);
            btnCreate.Name = "btnCreate";
            btnCreate.Size = new Size(103, 31);
            btnCreate.TabIndex = 7;
            btnCreate.Text = "Create";
            btnCreate.UseVisualStyleBackColor = true;
            btnCreate.Click += btnCreate_Click;
            // 
            // btnShowAB
            // 
            btnShowAB.Location = new Point(659, 195);
            btnShowAB.Margin = new Padding(3, 2, 3, 2);
            btnShowAB.Name = "btnShowAB";
            btnShowAB.Size = new Size(91, 32);
            btnShowAB.TabIndex = 8;
            btnShowAB.Text = "ShowAB";
            btnShowAB.UseVisualStyleBackColor = true;
            btnShowAB.Click += btnShowAB_Click;
            // 
            // btnShowC
            // 
            btnShowC.Location = new Point(772, 198);
            btnShowC.Margin = new Padding(3, 2, 3, 2);
            btnShowC.Name = "btnShowC";
            btnShowC.Size = new Size(75, 29);
            btnShowC.TabIndex = 9;
            btnShowC.Text = "ShowC";
            btnShowC.UseVisualStyleBackColor = true;
            btnShowC.Click += btnShowC_Click;
            // 
            // lblTime
            // 
            lblTime.AutoSize = true;
            lblTime.Location = new Point(736, 60);
            lblTime.Name = "lblTime";
            lblTime.Size = new Size(65, 20);
            lblTime.TabIndex = 11;
            lblTime.Text = "              ";
            // 
            // btnSeq
            // 
            btnSeq.Location = new Point(532, 255);
            btnSeq.Margin = new Padding(3, 2, 3, 2);
            btnSeq.Name = "btnSeq";
            btnSeq.Size = new Size(103, 35);
            btnSeq.TabIndex = 12;
            btnSeq.Text = "Seq";
            btnSeq.UseVisualStyleBackColor = true;
            btnSeq.Click += btnSeq_Click;
            // 
            // btnPar
            // 
            btnPar.Location = new Point(659, 255);
            btnPar.Margin = new Padding(3, 2, 3, 2);
            btnPar.Name = "btnPar";
            btnPar.Size = new Size(91, 35);
            btnPar.TabIndex = 13;
            btnPar.Text = "Par";
            btnPar.UseVisualStyleBackColor = true;
            btnPar.Click += btnPar_Click;
            // 
            // button1
            // 
            button1.Location = new Point(761, 255);
            button1.Margin = new Padding(3, 2, 3, 2);
            button1.Name = "button1";
            button1.Size = new Size(91, 35);
            button1.TabIndex = 14;
            button1.Text = "PF";
            button1.UseVisualStyleBackColor = true;
            button1.Click += button1_Click;
            // 
            // button2
            // 
            button2.Location = new Point(532, 321);
            button2.Margin = new Padding(3, 2, 3, 2);
            button2.Name = "button2";
            button2.Size = new Size(103, 35);
            button2.TabIndex = 15;
            button2.Text = "AVX";
            button2.UseVisualStyleBackColor = true;
            button2.Click += button2_Click;
            // 
            // SAWAF
            // 
            AutoScaleDimensions = new SizeF(8F, 20F);
            AutoScaleMode = AutoScaleMode.Font;
            ClientSize = new Size(864, 591);
            Controls.Add(button2);
            Controls.Add(button1);
            Controls.Add(btnPar);
            Controls.Add(btnSeq);
            Controls.Add(lblTime);
            Controls.Add(btnShowC);
            Controls.Add(btnShowAB);
            Controls.Add(btnCreate);
            Controls.Add(tb_p);
            Controls.Add(tbN);
            Controls.Add(tbB);
            Controls.Add(lbl_p);
            Controls.Add(lblN);
            Controls.Add(lblB);
            Controls.Add(dgArrs);
            Margin = new Padding(3, 2, 3, 2);
            Name = "SAWAF";
            Text = "Parallel Sum";
            ((System.ComponentModel.ISupportInitialize)dgArrs).EndInit();
            ResumeLayout(false);
            PerformLayout();

        }

        #endregion

        private System.Windows.Forms.DataGridView dgArrs;
        private System.Windows.Forms.DataGridViewTextBoxColumn ColA;
        private System.Windows.Forms.DataGridViewTextBoxColumn ColB;
        private System.Windows.Forms.DataGridViewTextBoxColumn ColC;
        private System.Windows.Forms.Label lblB;
        private System.Windows.Forms.Label lblN;
        private System.Windows.Forms.Label lbl_p;
        private System.Windows.Forms.TextBox tbB;
        private System.Windows.Forms.TextBox tbN;
        private System.Windows.Forms.TextBox tb_p;
        private System.Windows.Forms.Button btnCreate;
        private System.Windows.Forms.Button btnShowAB;
        private System.Windows.Forms.Button btnShowC;
        private System.Windows.Forms.Label lblTime;
        private System.Windows.Forms.Button btnSeq;
        private System.Windows.Forms.Button btnPar;
        private System.Windows.Forms.Button button1;
        private System.Windows.Forms.Button button2;
    }
}

