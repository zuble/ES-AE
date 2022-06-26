## Engenharia de Sistemas ~ Equipa AE


0. ### Install the requirements

       pip install -r requirements.txt

    ***

1. ### Run the Waypoints Coordinates Extractor script

       python map_coordinates_script.py --file coord.txt --image map.png

        --file Path to the image of the area where the boat is supposed to move
        --rad  Save the coordinates of the waypoins in radians (default is degrees)
        --file Path to .txt file with the reference coordinates

    - to **zoom in** hold the mouse right button & move it upwards

        release the mouse to apply it

    - to **zoom out** do the same but move it downwards 

    ***

2. ### Select the reference points in the order stated in the instructions image

	- Press the left button to select a point

	- If you make a mistake go back to 1

	- After selecting the 3 ref. points, press 0 to close the window

    ***

3. ### Select the waypoints however you want 

	- Press the left button to select a point

	- Press 0 after all the points are selected

    ***

4. ### The results will be saved in *waypoints.csv*

    ***

5. ### Run the GroundStation~USV IMC Communicator script

       python imc_gambini.py

        wp : Waypoints Description extrated from the .csv file

        start : IMC Plan Definition Phase + Vehicle Send 

        stop : not accuratte , Abort in Neptus

        exit : Terminate Actor loop