   M S B A M L   `   `   `  ����D  @Equalizer, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null!clr-namespace:WpfApp1WpfApp1  5   	       WpfApp1.MainWindow   5   	   W SPresentationCore, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35R NWindowsBase, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35\ XPresentationFramework, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35D 9http://schemas.microsoft.com/winfx/2006/xaml/presentation    5   	   R NSystem.Xaml, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089:x,http://schemas.microsoft.com/winfx/2006/xaml     5   	   @d2http://schemas.microsoft.com/expression/blend/2008     5   	   Jmc;http://schemas.openxmlformats.org/markup-compatibility/2006     5   	   'localclr-namespace:WpfApp1     5   	     � Title$  	Equalizer��5   	   $��479.285��6   $��856.518��6,   .��5	      �  � ColumnDefinitions 5
   
   �� 5      .+�5   
   �� -   5         ��Name$ Output��5      $	��168��6"   $��
25,96,24,0q�6/    �� TextWrapping$
 Wrap=�6C   $��Ready
��6W   $	��Top=�6n    �� 	IsEnabled .  �� IsReadOnlyCaretVisible . $��10(�6�   �� 5   
   -   5         ��Name$ StartButton��5      $
��Left=�6&   $	��Top=�6A   $	��800��6Y   $��
25,269,0,0q�6e   $��26��6y   $��Start��6�   6�   �� 5   
   $
��Left=�6   $��60��6/   $��	25,31,0,0q�6;   $
��Wrap=�6N   $	��Top=�6b   $	��800��6z   $��14(�6�   �� 6�   $�1) Press Start��6�   �� 6�   �� 6�   $(�"2) Select folder containing images��6�   �� 6�   �� 6�   $3�-3) When "Done!" message appears you can close��6�   6?  �� 5   
   -   5        $ CLAHEgridsize��5      $
��Left=�6)   $��20��6D   $��186,310,0,0q�6P   $
 Wrap=�6e   $��8��6y   $	��Top=�6�   $��61��6�   �� 5   
   -   5        $ BLURgridsize��5      $
��Left=�6(   $��19��6C   $��186,343,0,0q�6O   $
 Wrap=�6d   $��9��6x   $	��Top=�6�   $��61��6�   �� 5   
   -   5        $ 
clip_limit��5      $
��Left=�6&   $��21��6A   $��760,341,0,0q�6M   $
 Wrap=�6b   $	��2.0��6v   $	��Top=�6�   $��65��6�   �� 5   
   -   5        $ 
maskFactor��5      $
��Left=�6&   $��21��6A   $��760,310,0,0q�6M   $
 Wrap=�6b   $��3��6v   $	��Top=�6   $��65��6�   �� 5   
   $
��Left=�6   $��29��6+   $��
25,310,0,0q�67   $��CLAHE Grid Size (px)��6K   $	��Top=�6j   $	��156��6�   �� 5   
   $
��Left=�6   $��27��6+   $��
25,339,0,0q�67   $"��Gaussian Blur Grid Size (px)��6K   $	��Top=�6r   $	��156��6�   �� 5   
   $
��Left=�6   $��29��6+   $��284,337,0,0q�67   $��CLAHE Clip Limit��6L   $	��Top=�6g   $	��137��6   �� 5   
   $
��Left=�6   $��25��6+   $��284,310,0,0q�67   $<��6Unsharp Mask Factor [original image] / [blurred image]��6L   $	��Top=�6�   $	��471��6�   �� 5   
   -   5        $ 	blurSigma��5      $
��Left=�6%   $��21��6@   $��760,374,0,0q�6L   $
 Wrap=�6a   $��10��6u   $	��Top=�6   $��65��6�   �� 5   
   $
��Left=�6   $��26��6+   $��284,369,0,0q�67   $"��Gaussian Blur Radius (Sigma)��6L   $	��Top=�6s   $	��454��6�   �� 5   
   -   5        $ exportQuality��5      $
��Left=�6)   $��21��6D   $��186,373,0,0q�6P   $
 Wrap=�6e   $��90��6y   $	��Top=�6�   $��61��6�   �� 5   
   $��Export Quality (jpg)��6   $
��Left=�6/   $��26��6J   $��
25,369,0,0q�6V   $	��Top=�6j   $	��147��6�   �� 5   
   -	   5         ��Name$ SmartSharpen��5      $v��pUse smart sharpening? (reduces noise but also textural details, keep on for landscapes, off for macros/textures)��6)   $
��Left=�6�   $��21��6�   $��
25,400,0,0q�6�   $	��Top=�6�   $	��800��6�    d� 	IsChecked$
 TrueY�6  5      5      