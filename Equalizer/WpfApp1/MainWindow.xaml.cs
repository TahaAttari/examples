using Emgu.CV;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.IO;
using System.Threading;
using System.Windows;
using System.Windows.Forms;

namespace WpfApp1
{
    /// <summary>
    /// Equalizer takes an image and applies CLAHE for lighting and 
    /// and unsharp mask for sharpness. The parameters are generalized 
    /// to allow easy usage.
    /// 
    /// The program uses the EMGU wrapper to call OpenCV functions in
    /// C#.
    /// 
    /// Later, ideally, the parameters will be modifiable for greater
    /// control.
    /// 
    /// </summary>
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
        }

        private void StartButton_Click(object sender, EventArgs e)
        {
            //Get files-----------------------------------------------------------------
            FolderBrowserDialog fbd = new FolderBrowserDialog();
            DialogResult result = fbd.ShowDialog();
            if (result != System.Windows.Forms.DialogResult.OK || string.IsNullOrWhiteSpace(fbd.SelectedPath))
            {
                System.Windows.MessageBox.Show("Folder Invalid, please select again");
                return;
            }

            

            string[] jpg_list = Directory.GetFiles(fbd.SelectedPath, "*.jpg");
            int jpg_list_length = jpg_list.Length;

            if(jpg_list_length == 0)
            {
                System.Windows.MessageBox.Show("No jpgs found, please select again");
                return;
            }

            System.Diagnostics.Debug.WriteLine("There are " + Convert.ToString(jpg_list_length) + " jpg files in folder \n");
            Output.AppendText("There are " + Convert.ToString(jpg_list_length) + " jpg files in folder \n");

            int clahe_size;
            int blur_grid_size;
            int quality;

            //Set parameters-------------------------------------------------------------

            try
            {
                clahe_size = Convert.ToInt16(CLAHEgridsize.Text);
                Output.AppendText("clahe size = " + Convert.ToString(clahe_size));

                blur_grid_size = Convert.ToInt16(BLURgridsize.Text);
                if (blur_grid_size % 2 != 1)
                {
                    System.Windows.MessageBox.Show("blur grid size must be odd");
                    return;
                }
                Output.AppendText("blur grid size = " + Convert.ToString(blur_grid_size));

                quality = Convert.ToInt16(exportQuality.Text);
                Output.AppendText("quality = " + Convert.ToString(quality));

            }
            catch
            {
                System.Windows.MessageBox.Show("CLAHE size, blur grid size and quality must be integer values");
                return;
            }

            System.Drawing.Size claheGridSize = new System.Drawing.Size(clahe_size, clahe_size);
            System.Drawing.Size blur_size = new System.Drawing.Size(blur_grid_size, blur_grid_size);
            KeyValuePair<Emgu.CV.CvEnum.ImwriteFlags, int> outputQuality = new KeyValuePair<Emgu.CV.CvEnum.ImwriteFlags, int>(Emgu.CV.CvEnum.ImwriteFlags.JpegQuality, quality);

            double clipLimit;
            double alpha;
            double beta;
            double unsharp_factor;
            double gamma = 0;
            double sigma;
            double deviation = 0.33;
            double threshold1 = 128 * (1 - deviation);
            double threshold2 = 128 * (1 + deviation);

            try
            {
                clipLimit = Convert.ToDouble(clip_limit.Text);
                Output.AppendText("cliplimit = "+Convert.ToString(clipLimit));

                unsharp_factor = Convert.ToDouble(maskFactor.Text);

                beta = Math.Pow((-1 * unsharp_factor + 1), -1);
                Output.AppendText("beta = " + Convert.ToString(beta));

                alpha = 1 - beta;
                Output.AppendText("alpha = " + Convert.ToString(alpha));

                sigma = Convert.ToDouble(blurSigma.Text);
                Output.AppendText("sigma = " + Convert.ToString(sigma));
            }
            catch
            {
                System.Windows.MessageBox.Show("Clip Limit, Unsharp Factor and Sigma must be float values");
                return;
            }

            char[] period = { '.' };
            string[] splitname;

            Mat img = new Mat();
            Mat LAB = new Mat();
            Mat[] splitLAB;
            Mat afterClahe = new Mat();
            Mat rgbAgain = new Mat();
            Mat Blur = new Mat();
            Mat Unsharp = new Mat();
            Mat mask = new Mat();
            
            Matrix<byte> dilateKernel = new Matrix<byte>(new Byte[3, 3] { { 1, 0, 1 }, { 0, 1, 0 }, { 1, 0, 1 } });
            Matrix<byte> erodeKernel = new Matrix<byte>(new Byte[3, 3] { { 0, 1, 0 }, { 1, 0, 1 }, { 0, 1, 0 } });

            //Main script--------------------------------------------------------------------
            for (int i = 0; i < jpg_list_length; i++)
            {
                System.Diagnostics.Debug.WriteLine("now processing " + jpg_list[i]);
                Output.AppendText("now processing " + jpg_list[i] + "\n");
                splitname = jpg_list[i].Split(period);
                Output.UpdateLayout();
                //#-----Reading the image-----------------------------------------------------
                img = CvInvoke.Imread(jpg_list[i], Emgu.CV.CvEnum.ImreadModes.Color);

                //#-----Converting image to LAB Color model----------------------------------- 
                CvInvoke.CvtColor(img, LAB, Emgu.CV.CvEnum.ColorConversion.Bgr2Lab);

                //#-----Splitting the LAB image to different channels-------------------------
                splitLAB = LAB.Split();

                //#-----Applying CLAHE to L-channel-------------------------------------------
                CvInvoke.CLAHE(splitLAB[0], clipLimit, claheGridSize, splitLAB[0]);

                //#-----Merge the CLAHE enhanced L-channel with the a and b channel-----------
                CvInvoke.Merge(new Emgu.CV.Util.VectorOfMat(splitLAB[0],splitLAB[1],splitLAB[2]), afterClahe);

                //#-----Converting image from LAB Color model to RGB model--------------------
                CvInvoke.CvtColor(afterClahe, rgbAgain, Emgu.CV.CvEnum.ColorConversion.Lab2Bgr);             

                //#-----First part of Unsharp mask is to blur the image------------------------
                CvInvoke.GaussianBlur(rgbAgain, Blur, blur_size, sigma);

                //#-----Then subtract from original (beta is negative)--------------------------
                //#----- addweighted = (alpha*orignal) + (beta*blur) + gamma -------------------
                CvInvoke.AddWeighted(rgbAgain, alpha, Blur, beta, gamma, Unsharp);

                //#-----SmartSharpening avoids inflating noise---------------- -----------------
                if (SmartSharpen.IsChecked.GetValueOrDefault())
                {
                    //#-----Use Canny edge-finding to create mask with detailed features--------
                    CvInvoke.Canny(splitLAB[0], mask, threshold1, threshold2);

                    //#-----Grow mask (Canny outputs 1px lines)---------------------------------
                    CvInvoke.Dilate(mask, mask, dilateKernel, new System.Drawing.Point(-1, -1), 4, Emgu.CV.CvEnum.BorderType.Default, new Emgu.CV.Structure.MCvScalar());

                    //#-----Selectively copy sharpened image pixels------------------------------
                    Unsharp.CopyTo(rgbAgain, mask);

                    //#-----Save image-----------------------------------------------------------
                    CvInvoke.Imwrite(splitname[0] + "-equalized-smart.jpg", rgbAgain, outputQuality);
                }
                else
                {
                    //#-----Save image--------------------------------------------------------------
                    CvInvoke.Imwrite(splitname[0] + "-equalized.jpg", Unsharp, outputQuality);
                }
            }
            Output.AppendText("\n" + "Done! \n");
            return;
        }
    }
}
