namespace AMM
{
    partial class AMMF
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
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
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.dgB = new System.Windows.Forms.DataGridView();
            this.dgC = new System.Windows.Forms.DataGridView();
            this.dgA = new System.Windows.Forms.DataGridView();
            this.btnInit = new System.Windows.Forms.Button();
            this.tbN = new System.Windows.Forms.TextBox();
            this.btnAdd = new System.Windows.Forms.Button();
            this.btnInitBool = new System.Windows.Forms.Button();
            this.btnAddBool = new System.Windows.Forms.Button();
            this.btnClearInt = new System.Windows.Forms.Button();
            this.lblN = new System.Windows.Forms.Label();
            this.btnMultInt = new System.Windows.Forms.Button();
            this.btnMultBool = new System.Windows.Forms.Button();
            this.btnFloydShortest = new System.Windows.Forms.Button();
            this.btnFloydLongest = new System.Windows.Forms.Button();
            this.btnShortestPath = new System.Windows.Forms.Button();
            this.btnConnectivity = new System.Windows.Forms.Button();
            this.tbFrom = new System.Windows.Forms.TextBox();
            this.tbTo = new System.Windows.Forms.TextBox();
            this.lblFrom = new System.Windows.Forms.Label();
            this.lblTo = new System.Windows.Forms.Label();
            ((System.ComponentModel.ISupportInitialize)(this.dgB)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.dgC)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.dgA)).BeginInit();
            this.SuspendLayout();
            // 
            // dgB
            // 
            this.dgB.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dgB.ColumnHeadersVisible = false;
            this.dgB.Location = new System.Drawing.Point(385, 15);
            this.dgB.Margin = new System.Windows.Forms.Padding(4);
            this.dgB.Name = "dgB";
            this.dgB.RowHeadersVisible = false;
            this.dgB.RowHeadersWidth = 51;
            this.dgB.Size = new System.Drawing.Size(348, 311);
            this.dgB.TabIndex = 1;
            this.dgB.CellContentClick += new System.Windows.Forms.DataGridViewCellEventHandler(this.dgB_CellContentClick);
            // 
            // dgC
            // 
            this.dgC.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dgC.ColumnHeadersVisible = false;
            this.dgC.Location = new System.Drawing.Point(760, 15);
            this.dgC.Margin = new System.Windows.Forms.Padding(4);
            this.dgC.Name = "dgC";
            this.dgC.RowHeadersVisible = false;
            this.dgC.RowHeadersWidth = 51;
            this.dgC.Size = new System.Drawing.Size(347, 308);
            this.dgC.TabIndex = 2;
            // 
            // dgA
            // 
            this.dgA.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dgA.ColumnHeadersVisible = false;
            this.dgA.Location = new System.Drawing.Point(27, 15);
            this.dgA.Margin = new System.Windows.Forms.Padding(4);
            this.dgA.Name = "dgA";
            this.dgA.RowHeadersVisible = false;
            this.dgA.RowHeadersWidth = 51;
            this.dgA.Size = new System.Drawing.Size(328, 311);
            this.dgA.TabIndex = 0;
            // 
            // btnInit
            // 
            this.btnInit.Location = new System.Drawing.Point(33, 400);
            this.btnInit.Margin = new System.Windows.Forms.Padding(4);
            this.btnInit.Name = "btnInit";
            this.btnInit.Size = new System.Drawing.Size(111, 30);
            this.btnInit.TabIndex = 3;
            this.btnInit.Text = "InitInt";
            this.btnInit.UseVisualStyleBackColor = true;
            this.btnInit.Click += new System.EventHandler(this.btnInit_Click);
            // 
            // tbN
            // 
            this.tbN.Location = new System.Drawing.Point(87, 346);
            this.tbN.Margin = new System.Windows.Forms.Padding(4);
            this.tbN.Name = "tbN";
            this.tbN.Size = new System.Drawing.Size(56, 22);
            this.tbN.TabIndex = 4;
            // 
            // btnAdd
            // 
            this.btnAdd.Location = new System.Drawing.Point(168, 400);
            this.btnAdd.Margin = new System.Windows.Forms.Padding(4);
            this.btnAdd.Name = "btnAdd";
            this.btnAdd.Size = new System.Drawing.Size(100, 28);
            this.btnAdd.TabIndex = 5;
            this.btnAdd.Text = "AddInt";
            this.btnAdd.UseVisualStyleBackColor = true;
            this.btnAdd.Click += new System.EventHandler(this.btnAdd_Click);
            // 
            // btnInitBool
            // 
            this.btnInitBool.Location = new System.Drawing.Point(33, 437);
            this.btnInitBool.Margin = new System.Windows.Forms.Padding(4);
            this.btnInitBool.Name = "btnInitBool";
            this.btnInitBool.Size = new System.Drawing.Size(111, 28);
            this.btnInitBool.TabIndex = 6;
            this.btnInitBool.Text = "InitBool";
            this.btnInitBool.UseVisualStyleBackColor = true;
            this.btnInitBool.Click += new System.EventHandler(this.btnInitBool_Click);
            // 
            // btnAddBool
            // 
            this.btnAddBool.Location = new System.Drawing.Point(168, 437);
            this.btnAddBool.Margin = new System.Windows.Forms.Padding(4);
            this.btnAddBool.Name = "btnAddBool";
            this.btnAddBool.Size = new System.Drawing.Size(100, 28);
            this.btnAddBool.TabIndex = 7;
            this.btnAddBool.Text = "AddBool";
            this.btnAddBool.UseVisualStyleBackColor = true;
            this.btnAddBool.Click += new System.EventHandler(this.btnAddBool_Click);
            // 
            // btnClearInt
            // 
            this.btnClearInt.Location = new System.Drawing.Point(168, 347);
            this.btnClearInt.Margin = new System.Windows.Forms.Padding(4);
            this.btnClearInt.Name = "btnClearInt";
            this.btnClearInt.Size = new System.Drawing.Size(100, 28);
            this.btnClearInt.TabIndex = 8;
            this.btnClearInt.Text = "Clear";
            this.btnClearInt.UseVisualStyleBackColor = true;
            this.btnClearInt.Click += new System.EventHandler(this.btnClearInt_Click);
            // 
            // lblN
            // 
            this.lblN.AutoSize = true;
            this.lblN.Location = new System.Drawing.Point(39, 347);
            this.lblN.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.lblN.Name = "lblN";
            this.lblN.Size = new System.Drawing.Size(17, 16);
            this.lblN.TabIndex = 10;
            this.lblN.Text = "N";
            // 
            // btnMultInt
            // 
            this.btnMultInt.Location = new System.Drawing.Point(309, 401);
            this.btnMultInt.Margin = new System.Windows.Forms.Padding(4);
            this.btnMultInt.Name = "btnMultInt";
            this.btnMultInt.Size = new System.Drawing.Size(120, 26);
            this.btnMultInt.TabIndex = 11;
            this.btnMultInt.Text = "MultInt";
            this.btnMultInt.UseVisualStyleBackColor = true;
            this.btnMultInt.Click += new System.EventHandler(this.btnMultInt_Click);
            // 
            // btnMultBool
            // 
            this.btnMultBool.Location = new System.Drawing.Point(313, 434);
            this.btnMultBool.Margin = new System.Windows.Forms.Padding(4);
            this.btnMultBool.Name = "btnMultBool";
            this.btnMultBool.Size = new System.Drawing.Size(115, 30);
            this.btnMultBool.TabIndex = 12;
            this.btnMultBool.Text = "MultBool";
            this.btnMultBool.UseVisualStyleBackColor = true;
            this.btnMultBool.Click += new System.EventHandler(this.btnMultBool_Click);
            // 
            // btnFloydShortest
            // 
            this.btnFloydShortest.Location = new System.Drawing.Point(460, 347);
            this.btnFloydShortest.Margin = new System.Windows.Forms.Padding(4);
            this.btnFloydShortest.Name = "btnFloydShortest";
            this.btnFloydShortest.Size = new System.Drawing.Size(150, 28);
            this.btnFloydShortest.TabIndex = 13;
            this.btnFloydShortest.Text = "Floyd Shortest";
            this.btnFloydShortest.UseVisualStyleBackColor = true;
            this.btnFloydShortest.Click += new System.EventHandler(this.btnFloydShortest_Click);
            // 
            // btnFloydLongest
            // 
            this.btnFloydLongest.Location = new System.Drawing.Point(618, 347);
            this.btnFloydLongest.Margin = new System.Windows.Forms.Padding(4);
            this.btnFloydLongest.Name = "btnFloydLongest";
            this.btnFloydLongest.Size = new System.Drawing.Size(150, 28);
            this.btnFloydLongest.TabIndex = 14;
            this.btnFloydLongest.Text = "Floyd Longest";
            this.btnFloydLongest.UseVisualStyleBackColor = true;
            this.btnFloydLongest.Click += new System.EventHandler(this.btnFloydLongest_Click);
            // 
            // btnShortestPath
            // 
            this.btnShortestPath.Location = new System.Drawing.Point(776, 347);
            this.btnShortestPath.Margin = new System.Windows.Forms.Padding(4);
            this.btnShortestPath.Name = "btnShortestPath";
            this.btnShortestPath.Size = new System.Drawing.Size(150, 28);
            this.btnShortestPath.TabIndex = 15;
            this.btnShortestPath.Text = "Shortest Path";
            this.btnShortestPath.UseVisualStyleBackColor = true;
            this.btnShortestPath.Click += new System.EventHandler(this.btnShortestPath_Click);
            // 
            // btnConnectivity
            // 
            this.btnConnectivity.Location = new System.Drawing.Point(934, 347);
            this.btnConnectivity.Margin = new System.Windows.Forms.Padding(4);
            this.btnConnectivity.Name = "btnConnectivity";
            this.btnConnectivity.Size = new System.Drawing.Size(150, 28);
            this.btnConnectivity.TabIndex = 16;
            this.btnConnectivity.Text = "Connectivity";
            this.btnConnectivity.UseVisualStyleBackColor = true;
            this.btnConnectivity.Click += new System.EventHandler(this.btnConnectivity_Click);
            // 
            // tbFrom
            // 
            this.tbFrom.Location = new System.Drawing.Point(546, 390);
            this.tbFrom.Margin = new System.Windows.Forms.Padding(4);
            this.tbFrom.Name = "tbFrom";
            this.tbFrom.Size = new System.Drawing.Size(44, 22);
            this.tbFrom.TabIndex = 17;
            // 
            // tbTo
            // 
            this.tbTo.Location = new System.Drawing.Point(655, 390);
            this.tbTo.Margin = new System.Windows.Forms.Padding(4);
            this.tbTo.Name = "tbTo";
            this.tbTo.Size = new System.Drawing.Size(44, 22);
            this.tbTo.TabIndex = 18;
            // 
            // lblFrom
            // 
            this.lblFrom.AutoSize = true;
            this.lblFrom.Location = new System.Drawing.Point(501, 393);
            this.lblFrom.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.lblFrom.Name = "lblFrom";
            this.lblFrom.Size = new System.Drawing.Size(39, 16);
            this.lblFrom.TabIndex = 19;
            this.lblFrom.Text = "From";
            // 
            // lblTo
            // 
            this.lblTo.AutoSize = true;
            this.lblTo.Location = new System.Drawing.Point(622, 393);
            this.lblTo.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.lblTo.Name = "lblTo";
            this.lblTo.Size = new System.Drawing.Size(25, 16);
            this.lblTo.TabIndex = 20;
            this.lblTo.Text = "To";
            // 
            // AMMF
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(8F, 16F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1133, 490);
            this.Controls.Add(this.lblTo);
            this.Controls.Add(this.lblFrom);
            this.Controls.Add(this.tbTo);
            this.Controls.Add(this.tbFrom);
            this.Controls.Add(this.btnConnectivity);
            this.Controls.Add(this.btnShortestPath);
            this.Controls.Add(this.btnFloydLongest);
            this.Controls.Add(this.btnFloydShortest);
            this.Controls.Add(this.btnMultBool);
            this.Controls.Add(this.btnMultInt);
            this.Controls.Add(this.lblN);
            this.Controls.Add(this.btnClearInt);
            this.Controls.Add(this.btnAddBool);
            this.Controls.Add(this.btnInitBool);
            this.Controls.Add(this.btnAdd);
            this.Controls.Add(this.tbN);
            this.Controls.Add(this.btnInit);
            this.Controls.Add(this.dgC);
            this.Controls.Add(this.dgB);
            this.Controls.Add(this.dgA);
            this.Margin = new System.Windows.Forms.Padding(4);
            this.Name = "AMMF";
            this.Text = "AMM";
            ((System.ComponentModel.ISupportInitialize)(this.dgB)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.dgC)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.dgA)).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.DataGridView dgB;
        private System.Windows.Forms.DataGridView dgC;
        private System.Windows.Forms.DataGridView dgA;
        private System.Windows.Forms.Button btnInit;
        private System.Windows.Forms.TextBox tbN;
        private System.Windows.Forms.Button btnAdd;
        private System.Windows.Forms.Button btnInitBool;
        private System.Windows.Forms.Button btnAddBool;
        private System.Windows.Forms.Button btnClearInt;
        private System.Windows.Forms.Label lblN;
        private System.Windows.Forms.Button btnMultInt;
        private System.Windows.Forms.Button btnMultBool;
        private System.Windows.Forms.Button btnFloydShortest;
        private System.Windows.Forms.Button btnFloydLongest;
        private System.Windows.Forms.Button btnShortestPath;
        private System.Windows.Forms.Button btnConnectivity;
        private System.Windows.Forms.TextBox tbFrom;
        private System.Windows.Forms.TextBox tbTo;
        private System.Windows.Forms.Label lblFrom;
        private System.Windows.Forms.Label lblTo;
    }
}
