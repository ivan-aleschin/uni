using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace Chat
{
    public partial class ChatF : Form
    {
        ChatC ChC = new ChatC();

        public ChatF()
        {
            InitializeComponent();
        }

        private void btnLoad_Click(object sender, EventArgs e)
        {
            ChC.Load(rtbChat, tmrSem);          
        }

        private void btnSave_Click(object sender, EventArgs e)
        {
            ChC.Save(rtbChat);//rtbChat.SaveFile("Grasshopper.rtf");
        }

        private void tmrSem_Tick(object sender, EventArgs e)
        {
            ChC.Load(rtbChat, tmrSem); 
        }
    }
}
