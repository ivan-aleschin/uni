namespace ParallelJoinLab
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
            this.btnGenerateData = new System.Windows.Forms.Button();
            this.btnCreateSorted = new System.Windows.Forms.Button();
            this.btnCompareJoins = new System.Windows.Forms.Button();
            this.listBoxResults = new System.Windows.Forms.ListBox();
            this.lblStandardTime = new System.Windows.Forms.Label();
            this.lblParallelTime = new System.Windows.Forms.Label();
            this.lblStandardCount = new System.Windows.Forms.Label();
            this.lblParallelCount = new System.Windows.Forms.Label();
            this.btnShowDuplicates = new System.Windows.Forms.Button();
            this.txtStudentCount = new System.Windows.Forms.TextBox();
            this.txtCourseCount = new System.Windows.Forms.TextBox();
            this.label1 = new System.Windows.Forms.Label();
            this.label2 = new System.Windows.Forms.Label();
            this.lblSpeedup = new System.Windows.Forms.Label();
            this.lblStatus = new System.Windows.Forms.Label();
            this.lblMergeTime = new System.Windows.Forms.Label();
            this.lblMergeCount = new System.Windows.Forms.Label();
            this.lblValidation = new System.Windows.Forms.Label();
            this.SuspendLayout();
            // 
            // btnGenerateData
            // 
            this.btnGenerateData.Location = new System.Drawing.Point(12, 12);
            this.btnGenerateData.Name = "btnGenerateData";
            this.btnGenerateData.Size = new System.Drawing.Size(200, 30);
            this.btnGenerateData.TabIndex = 0;
            this.btnGenerateData.Text = "1. Сгенерировать тестовые данные";
            this.btnGenerateData.UseVisualStyleBackColor = true;
            this.btnGenerateData.Click += new System.EventHandler(this.btnGenerateData_Click);
            // 
            // btnCreateSorted
            // 
            this.btnCreateSorted.Location = new System.Drawing.Point(12, 48);
            this.btnCreateSorted.Name = "btnCreateSorted";
            this.btnCreateSorted.Size = new System.Drawing.Size(200, 30);
            this.btnCreateSorted.TabIndex = 1;
            this.btnCreateSorted.Text = "2. Создать отсортированные таблицы";
            this.btnCreateSorted.UseVisualStyleBackColor = true;
            this.btnCreateSorted.Click += new System.EventHandler(this.btnCreateSorted_Click);
            // 
            // btnCompareJoins
            // 
            this.btnCompareJoins.Location = new System.Drawing.Point(12, 84);
            this.btnCompareJoins.Name = "btnCompareJoins";
            this.btnCompareJoins.Size = new System.Drawing.Size(200, 30);
            this.btnCompareJoins.TabIndex = 2;
            this.btnCompareJoins.Text = "3. Сравнить Join алгоритмы";
            this.btnCompareJoins.UseVisualStyleBackColor = true;
            this.btnCompareJoins.Click += new System.EventHandler(this.btnCompareJoins_Click);
            // 
            // listBoxResults
            // 
            this.listBoxResults.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.listBoxResults.FormattingEnabled = true;
            this.listBoxResults.ItemHeight = 15;
            this.listBoxResults.Location = new System.Drawing.Point(218, 12);
            this.listBoxResults.Name = "listBoxResults";
            this.listBoxResults.Size = new System.Drawing.Size(570, 424);
            this.listBoxResults.TabIndex = 3;
            // 
            // lblStandardTime
            // 
            this.lblStandardTime.AutoSize = true;
            this.lblStandardTime.Location = new System.Drawing.Point(12, 130);
            this.lblStandardTime.Name = "lblStandardTime";
            this.lblStandardTime.Size = new System.Drawing.Size(112, 15);
            this.lblStandardTime.TabIndex = 4;
            this.lblStandardTime.Text = "Стандартный Join:";
            // 
            // lblParallelTime
            // 
            this.lblParallelTime.AutoSize = true;
            this.lblParallelTime.Location = new System.Drawing.Point(12, 180);
            this.lblParallelTime.Name = "lblParallelTime";
            this.lblParallelTime.Size = new System.Drawing.Size(106, 15);
            this.lblParallelTime.TabIndex = 5;
            this.lblParallelTime.Text = "Параллельный Join:";
            // 
            // lblStandardCount
            // 
            this.lblStandardCount.AutoSize = true;
            this.lblStandardCount.Location = new System.Drawing.Point(12, 145);
            this.lblStandardCount.Name = "lblStandardCount";
            this.lblStandardCount.Size = new System.Drawing.Size(104, 15);
            this.lblStandardCount.TabIndex = 6;
            this.lblStandardCount.Text = "Найдено записей:";
            // 
            // lblParallelCount
            // 
            this.lblParallelCount.AutoSize = true;
            this.lblParallelCount.Location = new System.Drawing.Point(12, 195);
            this.lblParallelCount.Name = "lblParallelCount";
            this.lblParallelCount.Size = new System.Drawing.Size(104, 15);
            this.lblParallelCount.TabIndex = 7;
            this.lblParallelCount.Text = "Найдено записей:";
            // 
            // btnShowDuplicates
            // 
            this.btnShowDuplicates.Location = new System.Drawing.Point(12, 300);
            this.btnShowDuplicates.Name = "btnShowDuplicates";
            this.btnShowDuplicates.Size = new System.Drawing.Size(200, 30);
            this.btnShowDuplicates.TabIndex = 8;
            this.btnShowDuplicates.Text = "Показать дубликаты ключей";
            this.btnShowDuplicates.UseVisualStyleBackColor = true;
            this.btnShowDuplicates.Click += new System.EventHandler(this.btnShowDuplicates_Click);
            // 
            // txtStudentCount
            // 
            this.txtStudentCount.Location = new System.Drawing.Point(120, 340);
            this.txtStudentCount.Name = "txtStudentCount";
            this.txtStudentCount.Size = new System.Drawing.Size(92, 23);
            this.txtStudentCount.TabIndex = 9;
            this.txtStudentCount.Text = "10000";
            // 
            // txtCourseCount
            // 
            this.txtCourseCount.Location = new System.Drawing.Point(120, 370);
            this.txtCourseCount.Name = "txtCourseCount";
            this.txtCourseCount.Size = new System.Drawing.Size(92, 23);
            this.txtCourseCount.TabIndex = 10;
            this.txtCourseCount.Text = "10000";
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(12, 343);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(102, 15);
            this.label1.TabIndex = 11;
            this.label1.Text = "Количество студентов:";
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(12, 373);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(91, 15);
            this.label2.TabIndex = 12;
            this.label2.Text = "Количество курсов:";
            // 
            // lblSpeedup
            // 
            this.lblSpeedup.AutoSize = true;
            this.lblSpeedup.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point);
            this.lblSpeedup.Location = new System.Drawing.Point(12, 220);
            this.lblSpeedup.Name = "lblSpeedup";
            this.lblSpeedup.Size = new System.Drawing.Size(71, 15);
            this.lblSpeedup.TabIndex = 13;
            this.lblSpeedup.Text = "Ускорение:";
            // 
            // lblStatus
            // 
            this.lblStatus.AutoSize = true;
            this.lblStatus.Location = new System.Drawing.Point(12, 420);
            this.lblStatus.Name = "lblStatus";
            this.lblStatus.Size = new System.Drawing.Size(44, 15);
            this.lblStatus.TabIndex = 14;
            this.lblStatus.Text = "Готово";
            // 
            // lblMergeTime
            // 
            this.lblMergeTime.AutoSize = true;
            this.lblMergeTime.Location = new System.Drawing.Point(12, 155);
            this.lblMergeTime.Name = "lblMergeTime";
            this.lblMergeTime.Size = new System.Drawing.Size(67, 15);
            this.lblMergeTime.TabIndex = 15;
            this.lblMergeTime.Text = "Merge Join:";
            // 
            // lblMergeCount
            // 
            this.lblMergeCount.AutoSize = true;
            this.lblMergeCount.Location = new System.Drawing.Point(12, 170);
            this.lblMergeCount.Name = "lblMergeCount";
            this.lblMergeCount.Size = new System.Drawing.Size(104, 15);
            this.lblMergeCount.TabIndex = 16;
            this.lblMergeCount.Text = "Найдено записей:";
            // 
            // lblValidation
            // 
            this.lblValidation.AutoSize = true;
            this.lblValidation.Location = new System.Drawing.Point(12, 240);
            this.lblValidation.Name = "lblValidation";
            this.lblValidation.Size = new System.Drawing.Size(127, 15);
            this.lblValidation.TabIndex = 17;
            this.lblValidation.Text = "Проверка корректности";
            // 
            // MainForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(7F, 15F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(800, 450);
            this.Controls.Add(this.lblValidation);
            this.Controls.Add(this.lblMergeCount);
            this.Controls.Add(this.lblMergeTime);
            this.Controls.Add(this.lblStatus);
            this.Controls.Add(this.lblSpeedup);
            this.Controls.Add(this.label2);
            this.Controls.Add(this.label1);
            this.Controls.Add(this.txtCourseCount);
            this.Controls.Add(this.txtStudentCount);
            this.Controls.Add(this.btnShowDuplicates);
            this.Controls.Add(this.lblParallelCount);
            this.Controls.Add(this.lblStandardCount);
            this.Controls.Add(this.lblParallelTime);
            this.Controls.Add(this.lblStandardTime);
            this.Controls.Add(this.listBoxResults);
            this.Controls.Add(this.btnCompareJoins);
            this.Controls.Add(this.btnCreateSorted);
            this.Controls.Add(this.btnGenerateData);
            this.Name = "MainForm";
            this.Text = "Parallel Join Lab";
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Button btnGenerateData;
        private System.Windows.Forms.Button btnCreateSorted;
        private System.Windows.Forms.Button btnCompareJoins;
        private System.Windows.Forms.ListBox listBoxResults;
        private System.Windows.Forms.Label lblStandardTime;
        private System.Windows.Forms.Label lblParallelTime;
        private System.Windows.Forms.Label lblStandardCount;
        private System.Windows.Forms.Label lblParallelCount;
        private System.Windows.Forms.Button btnShowDuplicates;
        private System.Windows.Forms.TextBox txtStudentCount;
        private System.Windows.Forms.TextBox txtCourseCount;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.Label lblSpeedup;
        private System.Windows.Forms.Label lblStatus;
        private System.Windows.Forms.Label lblMergeTime;
        private System.Windows.Forms.Label lblMergeCount;
        private System.Windows.Forms.Label lblValidation;
    }
}