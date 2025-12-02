#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>

// ======= CONFIG WIFI =======
const char* ssid = "Cristiano_2.4GHz";
const char* password = "01041980";
const char* serverURL = "http://192.168.1.35:8000/frame";

// ======= PINAGEM AI-THINKER (sem dependência externa) =======
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM     0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27

#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM       5

#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// ======= Config camera & helpers =======
void startCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  config.frame_size = FRAMESIZE_VGA; // FRAMESIZE_VGA
  config.jpeg_quality = 15;
  config.fb_count = 1;

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x\n", err);
    delay(2000);
    ESP.restart();
  }
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.printf("Conectando WiFi '%s' ...\n", ssid);
  uint32_t start = millis();
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(300);
    if (millis() - start > 20000) {
      Serial.println("\nFalha ao conectar no WiFi - reiniciando");
      ESP.restart();
    }
  }
  Serial.println("\nWiFi conectado!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());

  startCamera();
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi caiu, tentando reconectar...");
    WiFi.reconnect();
    delay(1000);
    return;
  }

  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Falha ao capturar frame");
    delay(1000);
    return;
  }

  HTTPClient http;
  http.begin(serverURL);
  http.addHeader("Content-Type", "image/jpeg");

  int httpCode = http.POST(fb->buf, fb->len);
  if (httpCode > 0) {
    Serial.printf("POST OK, code: %d, len: %d\n", httpCode, fb->len);
  } else {
    Serial.printf("POST falhou, error: %s\n", http.errorToString(httpCode).c_str());
  }
  http.end();

  esp_camera_fb_return(fb);

  delay(1000);
}
