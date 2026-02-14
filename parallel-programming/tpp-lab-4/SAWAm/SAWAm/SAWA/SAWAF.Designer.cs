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
            this.dgArrs = new System.Windows.Forms.DataGridView();
            this.ColA = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.ColB = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.ColC = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.lblB = new System.Windows.Forms.Label();
            this.lblN = new System.Windows.Forms.Label();
            this.lbl_p = new System.Windows.Forms.Label();
            this.tbB = new System.Windows.Forms.TextBox();
            this.tbN = new System.Windows.Forms.TextBox();
            this.tb_p = new System.Windows.Forms.TextBox();
            this.btnCreate = new System.Windows.Forms.Button();
            this.btnShowAB = new System.Windows.Forms.Button();
            this.btnShowC = new System.Windows.Forms.Button();
            this.lblTime = new System.Windows.Forms.Label();
            this.btnSeq = new System.Windows.Forms.Button();
            this.btnPar = new System.Windows.Forms.Button();
            ((System.ComponentModel.ISupportInitialize)(this.dgArrs)).BeginInit();
            this.SuspendLayout();
            // 
            // dgArrs
            // 
            this.dgArrs.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dgArrs.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] {
            this.ColA,
            this.ColB,
            this.ColC});
            this.dgArrs.Location = new System.Drawing.Point(9, 10);
            this.dgArrs.Margin = new System.Windows.Forms.Padding(2, 2, 2, 2);
            this.dgArrs.Name = "dgArrs";
            this.dgArrs.RowTemplate.Height = 24;
            this.dgArrs.Size = new System.Drawing.Size(352, 365);
            this.dgArrs.TabIndex = 0;
            // 
            // ColA
            // 
            this.ColA.HeaderText = "A";
            this.ColA.Name = "ColA";
            // 
            // ColB
            // 
            this.ColB.HeaderText = "B";
            this.ColB.Name = "ColB";
            // 
            // ColC
            // 
            this.ColC.HeaderText = "C";
            this.ColC.Name = "ColC";
            // 
            // lblB
            // 
            this.lblB.AutoSize = true;
            this.lblB.Location = new System.Drawing.Point(396, 40);
            this.lblB.Margin = new System.Windows.Forms.Padding(2, 0, 2, 0);
            this.lblB.Name = "lblB";
            this.lblB.Size = new System.Drawing.Size(14, 13);
            this.lblB.TabIndex = 1;
            this.lblB.Text = "B";
            // 
            // lblN
            // 
            this.lblN.AutoSize = true;
            this.lblN.Location = new System.Drawing.Point(395, 68);
            this.lblN.Margin = new System.Windows.Forms.Padding(2, 0, 2, 0);
            this.lblN.Name = "lblN";
            this.lblN.Size = new System.Drawing.Size(15, 13);
            this.lblN.TabIndex = 2;
            this.lblN.Text = "N";
            // 
            // lbl_p
            // 
            this.lbl_p.AutoSize = true;
            this.lbl_p.Location = new System.Drawing.Point(397, 101);
            this.lbl_p.Margin = new System.Windows.Forms.Padding(2, 0, 2, 0);
            this.lbl_p.Name = "lbl_p";
            this.lbl_p.Size = new System.Drawing.Size(13, 13);
            this.lbl_p.TabIndex = 3;
            this.lbl_p.Text = "p";
            // 
            // tbB
            // 
            this.tbB.Location = new System.Drawing.Point(438, 39);
            this.tbB.Margin = new System.Windows.Forms.Padding(2, 2, 2, 2);
            this.tbB.Name = "tbB";
            this.tbB.Size = new System.Drawing.Size(91, 20);
            this.tbB.TabIndex = 4;
            // 
            // tbN
            // 
            this.tbN.Location = new System.Drawing.Point(438, 68);
            this.tbN.Margin = new System.Windows.Forms.Padding(2, 2, 2, 2);
            this.tbN.Name = "tbN";
            this.tbN.Size = new System.Drawing.Size(90, 20);
            this.tbN.TabIndex = 5;
            // 
            // tb_p
            // 
            this.tb_p.Location = new System.Drawing.Point(439, 97);
            this.tb_p.Margin = new System.Windows.Forms.Padding(2, 2, 2, 2);
            this.tb_p.Name = "tb_p";
            this.tb_p.Size = new System.Drawing.Size(90, 20);
            this.tb_p.TabIndex = 6;
            // 
            // btnCreate
            // 
            this.btnCreate.Location = new System.Drawing.Point(399, 127);
            this.btnCreate.Margin = new System.Windows.Forms.Padding(2, 2, 2, 2);
            this.btnCreate.Name = "btnCreate";
            this.btnCreate.Size = new System.Drawing.Size(77, 20);
            this.btnCreate.TabIndex = 7;
            this.btnCreate.Text = "Create";
            this.btnCreate.UseVisualStyleBackColor = true;
            this.btnCreate.Click += new System.EventHandler(this.btnCreate_Click);
            // 
            // btnShowAB
            // 
            this.btnShowAB.Location = new System.Drawing.Point(494, 127);
            this.btnShowAB.Margin = new System.Windows.Forms.Padding(2, 2, 2, 2);
            this.btnShowAB.Name = "btnShowAB";
            this.btnShowAB.Size = new System.Drawing.Size(68, 21);
            this.btnShowAB.TabIndex = 8;
            this.btnShowAB.Text = "ShowAB";
            this.btnShowAB.UseVisualStyleBackColor = true;
            this.btnShowAB.Click += new System.EventHandler(this.btnShowAB_Click);
            // 
            // btnShowC
            // 
            this.btnShowC.Location = new System.Drawing.Point(579, 128);
            this.btnShowC.Margin = new System.Windows.Forms.Padding(2, 2, 2, 2);
            this.btnShowC.Name = "btnShowC";
            this.btnShowC.Size = new System.Drawing.Size(56, 19);
            this.btnShowC.TabIndex = 9;
            this.btnShowC.Text = "ShowC";
            this.btnShowC.UseVisualStyleBackColor = true;
            this.btnShowC.Click += new System.EventHandler(this.btnShowC_Click);
            // 
            // lblTime
            // 
            this.lblTime.AutoSize = true;
            this.lblTime.Location = new System.Drawing.Point(552, 39);
            this.lblTime.Margin = new System.Windows.Forms.Padding(2, 0, 2, 0);
            this.lblTime.Name = "lblTime";
            this.lblTime.Size = new System.Drawing.Size(49, 13);
            this.lblTime.TabIndex = 11;
            this.lblTime.Text = "              ";
            // 
            // btnSeq
            // 
            this.btnSeq.Location = new System.Drawing.Point(399, 166);
            this.btnSeq.Margin = new System.Windows.Forms.Padding(2, 2, 2, 2);
            this.btnSeq.Name = "btnSeq";
            this.btnSeq.Size = new System.Drawing.Size(77, 23);
            this.btnSeq.TabIndex = 12;
            this.btnSeq.Text = "Seq";
            this.btnSeq.UseVisualStyleBackColor = true;
            this.btnSeq.Click += new System.EventHandler(this.btnSeq_Click);
            // 
            // btnPar
            // 
            this.btnPar.Location = new System.Drawing.Point(503, 166);
            this.btnPar.Margin = new System.Windows.Forms.Padding(2, 2, 2, 2);
            this.btnPar.Name = "btnPar";
            this.btnPar.Size = new System.Drawing.Size(56, 19);
            this.btnPar.TabIndex = 13;
            this.btnPar.Text = "Par";
            this.btnPar.UseVisualStyleBackColor = true;
            this.btnPar.Click += new System.EventHandler(this.btnPar_Click);
            // 
            // SAWAF
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(648, 384);
            this.Controls.Add(this.btnPar);
            this.Controls.Add(this.btnSeq);
            this.Controls.Add(this.lblTime);
            this.Controls.Add(this.btnShowC);
            this.Controls.Add(this.btnShowAB);
            this.Controls.Add(this.btnCreate);
            this.Controls.Add(this.tb_p);
            this.Controls.Add(this.tbN);
            this.Controls.Add(this.tbB);
            this.Controls.Add(this.lbl_p);
            this.Controls.Add(this.lblN);
            this.Controls.Add(this.lblB);
            this.Controls.Add(this.dgArrs);
            this.Margin = new System.Windows.Forms.Padding(2, 2, 2, 2);
            this.Name = "SAWAF";
            this.Text = "Parallel Sum";
            ((System.ComponentModel.ISupportInitialize)(this.dgArrs)).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

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
    }
}

