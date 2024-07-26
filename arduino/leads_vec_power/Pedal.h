const int hallSensorPin = A0; // Analog pin connected to Hall sensor
float restValue = 0.157380254154448; // Variable for rest value
float maxValue = 0.697947214076246; // Variable for max value

// Function to map ADC value to a range between 0 and 1
float mapToRange(int adcValue, int adcMaxValue) {
    return (float)adcValue / adcMaxValue;
}
void setup() {
    Serial.begin(9600); // Initialize serial communication at 9600 bps
}
void loop() {
    // Read the ADC value from the Hall sensor
    int adcValue = analogRead(hallSensorPin);
    // Map the ADC value to a range between 0 and 1
    float pedalValue = (mapToRange(adcValue, 1023) - restValue) / maxValue;
    // Print the pedal value to the Serial Monitor
    Serial.print("Pedal Value: ");
    Serial.println(pedalValue, 2); // Print with 2 decimal places
    
    delay(500); // Delay for half a second
}