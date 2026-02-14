using System;
using System.IO;
using System.Windows.Forms;
using System.Threading;
using System.Diagnostics;

namespace Chat
{
    class ChatC
    {
        byte[] bSem = new byte[1];
        
        public void Load(RichTextBox _rtbChat, System.Windows.Forms.Timer _tmrSem)
        {
            bool SemAvail = false;

            // Use explicit path to ensure consistent working directory
            string semPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "Semaphore.txt");
            string grassPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "Grasshopper.rtf");

            while (!SemAvail)
            {
                try
                {
                    // Open for reading and allow others to read/write so we don't block readers.
                    using (var fSemR = File.Open(semPath, FileMode.Open, FileAccess.Read, FileShare.ReadWrite))
                    {
                        int read = fSemR.Read(bSem, 0, 1);
                        if (read == 0)
                        {
                            // Treat empty file as '0'
                            bSem[0] = (byte)'0';
                        }
                    }
                    SemAvail = true;
                }
                catch (FileNotFoundException)
                {
                    // Create semaphore file with '0' if it doesn't exist yet
                    bSem[0] = (byte)'0';
                    try
                    {
                        File.WriteAllBytes(semPath, bSem);
                        SemAvail = true;
                    }
                    catch (IOException ex)
                    {
                        // transient write failure; wait and retry
                        Debug.WriteLine(ex.ToString());
                        Thread.Sleep(50);
                    }
                }
                catch (IOException ex)
                {
                    // transient lock or IO issue — wait a bit and retry
                    Debug.WriteLine(ex.ToString());
                    Thread.Sleep(50);
                }
                catch (Exception ex)
                {
                    // unexpected error — log and rethrow
                    Debug.WriteLine(ex.ToString());
                    throw;
                }
            }

            // If semaphore is '0' -> enable timer (no content to show yet)
            if (bSem[0] == (byte)'0')
            {
                _tmrSem.Enabled = true;
            }
            else
            {
                // If semaphore is not '0', reset it to '0' and load the file
                bSem[0] = (byte)'0';
                try
                {
                    // Overwrite the semaphore file with '0' (exclusive write)
                    using (var fSemW = File.Open(semPath, FileMode.Create, FileAccess.Write, FileShare.None))
                    {
                        fSemW.Write(bSem, 0, 1);
                    }
                }
                catch (IOException ex)
                {
                    // best-effort: if we can't write semaphore back, record and continue
                    Debug.WriteLine(ex.ToString());
                }

                // Load the saved chat RTF if present
                if (File.Exists(grassPath))
                {
                    try
                    {
                        _rtbChat.LoadFile(grassPath);
                    }
                    catch (Exception ex)
                    {
                        // If LoadFile fails, leave textbox empty and record error
                        Debug.WriteLine(ex.ToString());
                    }
                }

                _tmrSem.Enabled = false;
            }           
        }
        public void Save(RichTextBox _rtbChat)
        {
            string semPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "Semaphore.txt");
            string grassPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "Grasshopper.rtf");

            // Save the RTF content first
            try
            {
                _rtbChat.SaveFile(grassPath);
            }
            catch (Exception ex)
            {
                Debug.WriteLine(ex.ToString());
                // If saving fails, still try to set semaphore
            }

            // Set semaphore to '1' (indicates new content / locked by writer)
            bSem[0] = (byte)'1';
            // Write with exclusive access so readers will observe a locked file and retry
            using (var fSemW = File.Open(semPath, FileMode.Create, FileAccess.Write, FileShare.None))
            {
                fSemW.Write(bSem, 0, 1);
            }
        }
    }
}
