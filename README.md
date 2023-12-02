# homeassistant helvar

This is a simple Home Assistant Integration for Helvar Lighting Systems.  Specifically the 9XX series Routers. 

All the heavy lifting is done by the [aiohelvar](https://github.com/tomplayford/aiohelvar) library.

## Features

You can control:
 - Individual lights (on DALI, DMX and SBUS)
   - Dimming, dimming over time
 - Groups
   - Setting scenes
     - Dimming between scenes, dimming over time
   - Relative and absolute adjustments to groups

The integration will receive push notifications (if you enable them on the router) about scene changes from the router. These are fed back to the entities state, so things show the current levels. Updates from individual devices are not sent by the router. 

For general use, this should cover most needs. I use it at home and it works well. 

## Installation

You'll need to install HACS first, then set this up as a custom repository.

## Usage

Enable the integration and you'll be prompted for your routers IP address and port. 

The integration will then pull all lighting devices, groups and scenes. 

- The lighting devices will be added as light entities.
- The groups will be added as select entities, and you'll be able to select from the group's available scenes.

## Limitations 

Many! But the following are probably the most significant:

  - Not tested with more than one Router (I only have one)
  - Not tested with RGB or WW/CW adjustable lights 
  - Helvar does not provide API access to input devices, so they're not available 
  - All the other limitations listed on the library README.
  - I'm sure there are bugs. 


## Help

I don't really like the Home Assistant select card scene integration - perhaps we need a custom one. Or integration with the HomeAssistant scenes setup. Not sure.

Submit to HomeAssistant. 


  ## Disclaimer

Halvar (TM) is a registered trademark of Helvar Ltd.

This software is not officially endorsed by Helvar Ltd. in any way.

The authors of this software provide no support, guarantees, or warranty for its use, features, safety, or suitability for any task. We do not recommend you use it for anything at all, and we don't accept any liability for any damages that may result from its use.

This software is licensed under the Apache License 2.0. See the LICENCE file for more details. 




