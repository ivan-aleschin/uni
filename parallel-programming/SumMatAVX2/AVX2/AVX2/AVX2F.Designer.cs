
namespace AVX2
{
    partial class AVX2F
    {
        /// <summary>
        ///  Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        ///  Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        ///  Required method for Designer support - do not modify
        ///  the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            btnStartArr = new System.Windows.Forms.Button();
            tbN = new System.Windows.Forms.TextBox();
            lblN = new System.Windows.Forms.Label();
            label1 = new System.Windows.Forms.Label();
            tb_p = new System.Windows.Forms.TextBox();
            btnStartMat = new System.Windows.Forms.Button();
            dgA = new System.Windows.Forms.DataGridView();
            dgB = new System.Windows.Forms.DataGridView();
            dgC = new System.Windows.Forms.DataGridView();
            btnShowMat = new System.Windows.Forms.Button();
            ((System.ComponentModel.ISupportInitialize)dgA).BeginInit();
            ((System.ComponentModel.ISupportInitialize)dgB).BeginInit();
            ((System.ComponentModel.ISupportInitialize)dgC).BeginInit();
            SuspendLayout();
            // 
            // btnStartArr
            // 
            btnStartArr.Location = new System.Drawing.Point(265, 46);
            btnStartArr.Name = "btnStartArr";
            btnStartArr.Size = new System.Drawing.Size(172, 29);
            btnStartArr.TabIndex = 0;
            btnStartArr.Text = "Start  Array Sum";
            btnStartArr.UseVisualStyleBackColor = true;
            btnStartArr.Click += btnStart_Click;
            // 
            // tbN
            // 
            tbN.Location = new System.Drawing.Point(98, 46);
            tbN.Name = "tbN";
            tbN.Size = new System.Drawing.Size(125, 27);
            tbN.TabIndex = 1;
            // 
            // lblN
            // 
            lblN.AutoSize = true;
            lblN.Location = new System.Drawing.Point(15, 46);
            lblN.Name = "lblN";
            lblN.Size = new System.Drawing.Size(20, 20);
            lblN.TabIndex = 2;
            lblN.Text = "N";
            // 
            // label1
            // 
            label1.AutoSize = true;
            label1.Location = new System.Drawing.Point(18, 119);
            label1.Name = "label1";
            label1.Size = new System.Drawing.Size(18, 20);
            label1.TabIndex = 3;
            label1.Text = "p";
            // 
            // tb_p
            // 
            tb_p.Location = new System.Drawing.Point(98, 117);
            tb_p.Name = "tb_p";
            tb_p.Size = new System.Drawing.Size(125, 27);
            tb_p.TabIndex = 4;
            // 
            // btnStartMat
            // 
            btnStartMat.Location = new System.Drawing.Point(265, 119);
            btnStartMat.Name = "btnStartMat";
            btnStartMat.Size = new System.Drawing.Size(165, 28);
            btnStartMat.TabIndex = 5;
            btnStartMat.Text = " Start Matrices Sum";
            btnStartMat.UseVisualStyleBackColor = true;
            btnStartMat.Click += btnStartMat_Click;
            // 
            // dgA
            // 
            dgA.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            dgA.Location = new System.Drawing.Point(12, 228);
            dgA.Name = "dgA";
            dgA.RowHeadersWidth = 51;
            dgA.RowTemplate.Height = 29;
            dgA.Size = new System.Drawing.Size(404, 473);
            dgA.TabIndex = 6;
            // 
            // dgB
            // 
            dgB.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            dgB.Location = new System.Drawing.Point(437, 228);
            dgB.Name = "dgB";
            dgB.RowHeadersWidth = 51;
            dgB.RowTemplate.Height = 29;
            dgB.Size = new System.Drawing.Size(417, 473);
            dgB.TabIndex = 7;
            // 
            // dgC
            // 
            dgC.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            dgC.Location = new System.Drawing.Point(870, 228);
            dgC.Name = "dgC";
            dgC.RowHeadersWidth = 51;
            dgC.RowTemplate.Height = 29;
            dgC.Size = new System.Drawing.Size(419, 473);
            dgC.TabIndex = 8;
            // 
            // btnShowMat
            // 
            btnShowMat.Location = new System.Drawing.Point(460, 122);
            btnShowMat.Name = "btnShowMat";
            btnShowMat.Size = new System.Drawing.Size(142, 26);
            btnShowMat.TabIndex = 9;
            btnShowMat.Text = "Show Matrices";
            btnShowMat.UseVisualStyleBackColor = true;
            btnShowMat.Click += btnShowMat_Click;
            // 
            // AVX2F
            // 
            AutoScaleDimensions = new System.Drawing.SizeF(8F, 20F);
            AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            ClientSize = new System.Drawing.Size(1303, 754);
            Controls.Add(btnShowMat);
            Controls.Add(dgC);
            Controls.Add(dgB);
            Controls.Add(dgA);
            Controls.Add(btnStartMat);
            Controls.Add(tb_p);
            Controls.Add(label1);
            Controls.Add(lblN);
            Controls.Add(tbN);
            Controls.Add(btnStartArr);
            Name = "AVX2F";
            Text = "AVX2";
            ((System.ComponentModel.ISupportInitialize)dgA).EndInit();
            ((System.ComponentModel.ISupportInitialize)dgB).EndInit();
            ((System.ComponentModel.ISupportInitialize)dgC).EndInit();
            ResumeLayout(false);
            PerformLayout();
        }

        #endregion

        private System.Windows.Forms.Button btnStartArr;
        private System.Windows.Forms.TextBox tbN;
        private System.Windows.Forms.Label lblN;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.TextBox tb_p;
        private System.Windows.Forms.Button btnStartMat;
        private System.Windows.Forms.DataGridView dgA;
        private System.Windows.Forms.DataGridView dgB;
        private System.Windows.Forms.DataGridView dgC;
        private System.Windows.Forms.Button btnShowMat;
    }
}
