# E-Waste Sorter for UGA

## The Problem

E-waste is one of the fastest-growing waste streams on college campuses. Most students don't know how to properly dispose of electronics, leading to improper handling and environmental impact.

## The Solution

We built an **AI-powered, automated e-waste sorter** designed specifically for UGA students. Our system makes proper e-waste disposal accessible to everyone.

## How It Works

1. **Place an item on the conveyor**  
   Students place an electronic item (such as batteries, cables, or small devices) onto the conveyor belt. No technical knowledge about electronics or recycling is required.

2. **On-device AI recognition**  
   A camera mounted above the conveyor captures an image of the item. A Raspberry Pi running an on-device machine learning model (YOLO-based object detection) identifies the type of e-waste in real time.

3. **Automated sorting**  
   Based on the model’s prediction, servo motors are actuated to route the item into the appropriate bin (e.g., hazardous batteries, electronic components, or accessories).

4. **Live web dashboard & local guidance**  
   The classification result is sent to a web dashboard where users can view:
   - The detected item type and confidence score  
   - Environmental and safety information  
   - Personalized disposal guidance using real local Georgia and UGA resources

## Key Features

- ✨ **Zero technical knowledge required** - Just place and go
- 🤖 **AI-powered identification** - Instantly recognizes electronics
- 📚 **Educational** - Learn proper disposal methods for each item type
- 🌍 **Local connections** - Access to real UGA-area e-waste disposal resources
- ⚡ **Fast & automated** - Efficient sorting process for high-volume campus use

## Getting Started

Place an electronic item on the belt and let our system do the work. Follow the on-screen guidance for disposal options available in the Athens, GA area.

## Support

For assistance or questions about e-waste disposal, reach out to our team or consult the educational resources provided by the sorter system.



## DEV SET UP
1. Clone the repo
2. Create a `.env` file in the root: GEMINI_API_KEY=your_api_key_here
3. Install dependencies: pip install -r requirements.txt
4. Create a Gemini API key:
   https://aistudio.google.com/app/apikey
5. Add your key:
   GEMINI_API_KEY=your_key_here
6. Run the app