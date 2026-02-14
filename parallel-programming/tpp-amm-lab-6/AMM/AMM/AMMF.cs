using System;
using System.Windows.Forms;

namespace AMM
{
    public partial class AMMF : Form
    {
        AMMRI RI = new AMMRI();
        AMMRB RB = new AMMRB();

        public AMMF()
        {
            InitializeComponent();
            tbN.Text = "5";
        }

        // --------- ОБЩЕЕ / СТАРОЕ ---------

        // Пустой обработчик, чтобы конструктор форм не ругался
        // на dgB_CellContentClick, который подписан в Designer.
        private void dgB_CellContentClick(object sender, DataGridViewCellEventArgs e)
        {
            // Ничего делать не нужно
        }

        // --------- ЦЕЛОЧИСЛЕННЫЕ МАТРИЦЫ (RI) ---------



        private void btnInit_Click(object sender, EventArgs e)
        {
            if (!RI.InitRnd(tbN.Text, dgA, dgB, dgC))
                MessageBox.Show("Некорректное N");
        }

        private void btnAdd_Click(object sender, EventArgs e)
        {
            RI.AddM();
            RI.Show(dgC);
        }

        private void btnMultInt_Click(object sender, EventArgs e)
        {
            RI.MultM();
            RI.Show(dgC);
        }

        private void btnClearInt_Click(object sender, EventArgs e)
        {
            for (int i = 0; i < dgA.RowCount; i++)
                for (int j = 0; j < dgA.ColumnCount; j++)
                {
                    dgA.Rows[i].Cells[j].Value = "";
                    dgB.Rows[i].Cells[j].Value = "";
                    dgC.Rows[i].Cells[j].Value = "";
                }
        }

        /// <summary>
        /// Флойд–Уоршелл: матрица всех кратчайших путей.
        /// rA трактуется как матрица весов.
        /// </summary>
        private void btnFloydShortest_Click(object sender, EventArgs e)
        {
            try
            {
                RI.UpdateAFromGrid(dgA);          // ← НОВОЕ
                RI.ComputeAllPairsShortestPaths();
                RI.Show(dgC);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Ошибка при вычислении кратчайших путей (Флойд): " + ex.Message);
            }
        }


        /// <summary>
        /// Флойд–Уоршелл: матрица всех длиннейших путей (учебный пример).
        /// </summary>
        private void btnFloydLongest_Click(object sender, EventArgs e)
        {
            try
            {
                RI.UpdateAFromGrid(dgA);          // ← НОВОЕ
                RI.ComputeAllPairsLongestPaths();
                RI.Show(dgC);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Ошибка при вычислении длиннейших путей (Флойд): " + ex.Message);
            }
        }


        /// <summary>
        /// Разузлование одного кратчайшего пути между вершинами from и to.
        /// </summary>
        private void btnShortestPath_Click(object sender, EventArgs e)
        {
            try
            {
                if (!int.TryParse(tbFrom.Text, out int from) ||
                    !int.TryParse(tbTo.Text, out int to))
                {
                    MessageBox.Show("Нужно ввести целые номера вершин в полях From и To.");
                    return;
                }

                RI.UpdateAFromGrid(dgA);          // ← НОВОЕ

                int[] path = RI.GetShortestPath(from, to);
                if (path == null || path.Length == 0)
                {
                    MessageBox.Show("Пути между выбранными вершинами нет.");
                    return;
                }

                string pathStr = string.Join(" -> ", path);
                MessageBox.Show("Кратчайший путь:\n" + pathStr);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Ошибка при разузловании пути: " + ex.Message);
            }
        }


        // --------- БУЛЕВЫЕ МАТРИЦЫ (RB) ---------

        private void btnInitBool_Click(object sender, EventArgs e)
        {
            if (!RB.InitRnd(tbN.Text, dgA, dgB, dgC))
                MessageBox.Show("Некорректное N");
        }

        private void btnAddBool_Click(object sender, EventArgs e)
        {
            // перечитываем A и B из dgA/dgB
            RB.UpdateABFromGrids(dgA, dgB);

            RB.AddM();
            RB.Show(dgC);
        }


        private void btnMultBool_Click(object sender, EventArgs e)
        {
            // перечитываем A и B из dgA/dgB
            RB.UpdateABFromGrids(dgA, dgB);

            RB.MultM();
            RB.Show(dgC);
        }


        /// <summary>
        /// Транзитивное замыкание (связность) булевой матрицы смежности.
        /// </summary>
        private void btnConnectivity_Click(object sender, EventArgs e)
        {
            try
            {
                RB.UpdateAFromGrid(dgA);          // ← НОВОЕ
                RB.ComputeConnectivityClosure();
                RB.Show(dgC);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Ошибка при вычислении связности графа: " + ex.Message);
            }
        }

    }
}
