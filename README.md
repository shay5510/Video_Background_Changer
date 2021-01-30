# Video_Background_Changer

<div class='explanation'>
  <h2>
    Quick Explanation
  </h2>
  <p>
    The following algorithm gets an input video from a stationary camera or a relatively stable video of a singe moving object.<br>
    The algorithm will extract the background and the object separately - with background substraction.<br>
    You can choose any background you want (image or video) and you will get a new video which combine the object and the new background.  
    * Project partner - Daniel Kozoyatov https://github.com/kozoyatov
  </p>
  <table style="width:100%">
  <tr>
    <th>Input: Original shaky video</th>
    <th colspan="2">Output: Stable video + changed BG + tracker</th>
  </tr>
  <tr>
    <td><img src="images/input.gif" width=400></td>
    <td><img src="images/output.gif" width=400></td>
  </tr>
</table>
</div>  
<div class='stabilization'>
  <h2>
    Stabilization
  </h2>
  <p>
    For get better results I recommend use a stationary camera.<tr>
    If you do not have a stationary camera try to film the video as stable as you can, then the following algorithm will stabilze your video.<tr> 
  
  </p>
    <div class='stabilization_algo'>
      <h4>
        Stabilization Algorithm:
      </h4>
      <ul>
        <li> The stabilization algorithm read the input video frame by frame.</li>
        <li>On each frame (frame_i) it using cv2.goodFeaturesToTrack to get the "interesting" points.</li>
      </ul>
      <p align="center">
        <img src="images/goodFeaturesToTrack.PNG" width=400></li>
      </p>  
      <ul>  
        <li>Then it is using cv2.calcOpticalFlowPyrLK where the input videos are: frame_i, frame_i+1,<tr>
        this functions gives us the matching points between two sequential frames.</li>
        <li>With cv2.findHomography we now have the transformation matrix between each two frames.</li>
        <li>For each element in the transform matrix we calculate his trajectory by doing cumulative sum between all tramsform          matrixes.</li>  
        <li>To get better results we will "smooth" the trajectory with moving average filter:</li>
      </ul>
      <p align="center">
              <img src="images/CodeCogsEqn.gif" width=250><br>
      <img src="images/smooth_curve.PNG" width=400>
      </p> 
    </div>  
    
  <table style="width:100%">
  <tr>
    <th>Input: unstable video</th>
    <th colspan="2">Output: stable video</th>
  </tr>
  <tr>
    <td><img src="images/input.gif" width=400></td>
    <td><img src="images/stable.gif" width=400></td>
   
  </tr>
</table>
</div>  
<div class='background'>
  <h2>
    Background Substraction  
  </h2> 
  <p>
  In this part we will extract the background without the object<tr> 
  </p>
  <ul>
    <li>We will randomly sample 50 frames from the original video and we will use Median filter for extracting the background.</li>
    <li>Now we will read the input video again and we will subtract the background from each frame.</li>
    <li>By using threshold on absolute subtraction value we got a binary mask.</li>
    <li>Finally we can extract the object by multiple each frame with the current mask.</li>
  </ul>  
  <p align="center">
    <img src="images/threshold.PNG" width=400><br>
  </p>  
  <table style="width:100%">
  <tr>
    <th>Binary Mask</th>
    <th colspan="2">Extracted</th>
  </tr>
  <tr>
    <td><img src="images/mask.gif" width=400></td>
    <td><img src="images/extracted.gif" width=400></td>
   
  </tr>
</table>
</div>

<div class='Matting'>
  <h2>
    Matting
  </h2> 
  <p>
  In this part we will work on Value plane (HSV).
  </p>
  
  <table style="width:100%">
    <tr>
      <th>From last section we got the binary mask, therefore we can easly extract the object.</th>
      <th colspan="2">The matting operation executed on the borders.</th>
    </tr>
    <tr>
      <td><img src="images/mask_initial.PNG" width=100></td>
      <td> <img src="images/alpha.PNG" width=100></td>
    </tr>
  </table>
  <ul>
    <li>We will calculate the PDF of the object - P(C|F) and the PDF of the background - P(C|B)</li>
    <li>Finally we will find the likelihood of each pixel (on the border) - if it belongs to BG or to the object.</li>
  </ul>
  <p align="center">
    <img src="images/likelihood.PNG" width=400>
  </p> 
  <ul>
    <li>After calculating the probability of each frame we will calculate the geodesic distance for each frame (from BG and from the object.</li>
    <li>Geodesic distance calculation executed with <a href="https://github.com/taigw/GeodisTKl">GeodisTKl</a>.</li>
  </ul>    
  <p align="center">
     <img src="images/Geo.PNG" width=400>
  </p> 
  <h3>Alpha</h3>
  <p>In this section we will calculate alpha matrix with the following formula:</p>
  <p align="center">
    <img src="images/alpha_formula.PNG" width=250>
  </p>
  <p>Alpha zoom in:</p>
  <p align="center">
     <img src="images/alpha_zoom_in.PNG" width=400>
  </p>
  <p>Finally we will get the new video with the following formula (frame by frame):</p>
  <p align="center">
    <img src="images/Vx.gif" width=200>
  </p>
  <p>Frame from final result:</p>
  <p align="center">
    <img src="images/final_res.PNG" width=300>
  </p>
</div>
