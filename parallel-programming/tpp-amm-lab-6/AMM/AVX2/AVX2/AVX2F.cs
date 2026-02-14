using System.Windows.Forms;

namespace AVX2
{
    public partial class AVX2F : Form
    {
        AVX2C sumArr = new AVX2C();
        public AVX2F()
        {
            InitializeComponent();
        }

        private void btnStart_Click(object sender, System.EventArgs e)
        {
            sumArr.Gen(tbN.Text);
        }
    }
}
