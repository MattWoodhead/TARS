#include <Adafruit_NeoPixel.h>
#include <ACAN2515Tiny.h>

static const byte MCP2515_CS  = 10 ; // CS input of MCP2515 (adapt to your design)
static const byte MCP2515_INT =  2 ; // INT output of MCP2515 (adapt to your design)

ACAN2515Tiny can (MCP2515_CS, SPI, MCP2515_INT) ;  // MCP2515 driver object
static const uint32_t QUARTZ_FREQUENCY = 16UL * 1000UL * 1000UL ;  // 16 MHz

uint32_t time_ms = millis();
uint8_t time_ms_bytes[4];
uint8_t msg_id_bytes[4];


void setup ()
{
  pinMode (LED_BUILTIN, OUTPUT) ;
  digitalWrite (LED_BUILTIN, LOW) ;
  Serial.begin (115200) ;
  while (!Serial)
  {
    delay (10) ;
    digitalWrite (LED_BUILTIN, !digitalRead (LED_BUILTIN)) ;
  }

  digitalWrite (LED_BUILTIN, LOW);

  SPI.begin () ;
  Serial.println ("Configure ACAN2515") ;
  ACAN2515TinySettings settings (QUARTZ_FREQUENCY, 250UL * 1000UL) ; // CAN bit rate 250 kb/s
  const uint16_t errorCode = can.begin (settings, [] { can.isr();});
  
  if (errorCode == 0)
  {
    Serial.print ("Bit Rate prescaler: ") ;
    Serial.println (settings.mBitRatePrescaler) ;
    Serial.print ("Propagation Segment: ") ;
    Serial.println (settings.mPropagationSegment) ;
    Serial.print ("Phase segment 1: ") ;
    Serial.println (settings.mPhaseSegment1) ;
    Serial.print ("Phase segment 2: ") ;
    Serial.println (settings.mPhaseSegment2) ;
    Serial.print ("SJW: ") ;
    Serial.println (settings.mSJW) ;
    Serial.print ("Triple Sampling: ") ;
    Serial.println (settings.mTripleSampling ? "yes" : "no") ;
    Serial.print ("Actual bit rate: ") ;
    Serial.print (settings.actualBitRate ()) ;
    Serial.println (" bit/s") ;
    Serial.print ("Exact bit rate ? ") ;
    Serial.println (settings.exactBitRate () ? "yes" : "no") ;
    Serial.print ("Sample point: ") ;
    Serial.print (settings.samplePointFromBitStart ()) ;
    Serial.println ("%") ;
  }
  else 
  {
    Serial.print ("Configuration error 0x") ;
    Serial.println (errorCode, HEX) ;
  }

  delay(2500);
}

void loop () {

  CANMessage frame;

  if (can.receive(frame)) {
    digitalWrite (LED_BUILTIN, !digitalRead (LED_BUILTIN)) ;
    Serial.write(0xAA);
    time_ms = millis();  // update to latest time
    memcpy(time_ms_bytes, &time_ms, 4);  // split the uint32_t into 4 bytes
    Serial.write(time_ms_bytes, 4);
    Serial.write(frame.len);
    memcpy(msg_id_bytes, &frame.id, 4);  // split the uint32_t into 4 bytes
    Serial.write(msg_id_bytes, 4);
    Serial.write(frame.data, frame.len);
    Serial.write(0xBB);
    Serial.println();
  }
}
