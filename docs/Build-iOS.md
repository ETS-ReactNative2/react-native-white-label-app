# iOS installation steps

**Note**: At this point, you should already have completed [Base app configuration](../README.md#base-app-configuration) section.

* [Steps](#steps)
* [Optional](#optional)
* [Issues](#issues)

## Steps

1. Open iOS project in Xcode and in Build Settings update `iOS deployment target` to 11.0. Also, change version in `Podfile`:

    ```ruby
        platform :ios, '11.0'
    ```

2. Create new swift file and add it to your Xcode project. When offered, also accept creating `*-Bridging-Header.h` file too. You can leave the content of both files empty.

3. Add VCX library:
    VCX Cocoapods library is necessary to be added to iOS Podfile.

      * Add the next source to the top of your Podfile:

        ```ruby
            ...
            source 'https://cdn.cocoapods.org/'
            source 'https://gitlab.com/evernym/mobile/mobile-sdk.git'
        ```

      * Add VCX dependency into your Podfile inside target <ProjectName>:
        * release build for devices only (`arm64`):

           ```ruby
            pod 'vcx', '0.0.227'
           ```

        * debug build for simulators

           ```ruby
                pod 'vcx', '0.0.228'
           ```

      * **Note** that currently recommended VCX versions are `227/228`.

      * Add below lines inside your `target` in Podfile
  
        ```ruby
            use_frameworks!
            $RNFirebaseAsStaticFramework = true
        ```

4. Add apptentive. You are not required to use this library. As of now we have a dependency on this library. We will make this optional in future. Add below dependency in `Podfile`
  
    `pod 'apptentive-ios'`

5. Run `pod install`

6. Configure App permissions by adding following lines to `ios/<project-name>/info.plist` file

    ```xml
        <key>NSCameraUsageDescription</key>
        <string>Please allow us access to Camera so that we can scan QR code</string>
        <key>NSFaceIDUsageDescription</key>
        <string>Enabling Face ID allows you quick and secure access to your app.</string>
        <key>NSMicrophoneUsageDescription</key>
        <string>Connect.Me uses your microphone to support audio messages.</string>
        <key>NSPhotoLibraryAddUsageDescription</key>
        <string>Connect.Me needs access to your photo library in order to set your avatar photo.</string>
        <key>NSPhotoLibraryUsageDescription</key>
        <string>Connect.Me needs access to your photo library in order to set your avatar photo.</string>
    ```

   > Remember to replace `Connect.Me` with your app name

7. Add below entries in same info.plist file

    ```xml
        <key>UIStatusBarHidden</key>
        <true/>
        <key>UISupportedInterfaceOrientations</key>
        <array>
            <string>UIInterfaceOrientationPortrait</string>
        </array>
        <key>UIViewControllerBasedStatusBarAppearance</key>
        <false/>
    ```

8. Open `awesomeMsdkProject.xcworkspace` in Xcode and set `Always embed swift binaries` to `Yes`

## Optional

### Push Notifications configuration

There are two strategies regarding receiving messages by an application which described [here](./Customization.md#receiving-message):

If you wish to use **Push Notifications** strategy you need to set variable `USE_PUSH_NOTIFICATION=true` and follow steps bellow to configure Firebase for iOS:

**Official documentation:** https://developer.apple.com/documentation/usernotifications

1. Add initialization of Firebase library into your `AppDelegate.m`:

    ```objectiveC
    # import Firebase framework
    # import <Firebase.h>
    
    @implementation AppDelegate
      - (BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)launchOptions {
            
            // ...
        
            if ([FIRApp defaultApp] == nil) {
              [FIRApp configure];
            }
        
            // ...
        
        return YES;
    }
    ```

1. Add Push notification capabilities.
1. When selected Xcode project, choose **Signing & Capabilities**. From there, select signing for valid **Team** and **bundle identifier**.
   Tap `+ Capabilty` and from the drop list (or by searching) choose `Push notifications`.
   New certificates and provision profiles should be automatically generated by Xcode.

  * Don't forget to follow rest of the steps for registering your app with Firebase service and including adding GoogleService-Info.plist to your project. For more details, please refer to official documentaion here: <a href="https://firebase.google.com/docs/cloud-messaging/ios/client" target="_blank" >https://firebase.google.com/docs/cloud-messaging/ios/client</a>

  * Register app for push notifications in AppDelegate.m

   ```objC
   if ([UNUserNotificationCenter class] != nil) {
     [UNUserNotificationCenter currentNotificationCenter].delegate = self;
     UNAuthorizationOptions authOptions = UNAuthorizationOptionAlert |
         UNAuthorizationOptionSound | UNAuthorizationOptionBadge;
     [[UNUserNotificationCenter currentNotificationCenter]
         requestAuthorizationWithOptions:authOptions
         completionHandler:^(BOOL granted, NSError * _Nullable error) {
           // ...
         }];
   }
   
   [application registerForRemoteNotifications];
   
   ```

1. Add below entries to `ios/<project-name>/info.plist` file

   ```xml
    <key>UIBackgroundModes</key>
    <array>
        <string>remote-notification</string>
    </array>
    <key>FirebaseScreenReportingEnabled</key>
    <false/>
    <key>firebase_crashlytics_collection_enabled</key>
    <false/>
   ```

### Deep linking configuration

If you want to add a capability where if user taps on a link in other apps (slack, email, whatsapp, etc.) and that link should open the app. Then you can add a deep linking configuration as described below. Evernym's react-native SDK uses branch.io for deep linking.

* In you `AppDelegate.m` add this line `#import "RNBranch.h"` in import statements
* In `AppDelegate.m` find the method `(BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)launchOptions`.
  * Inside this method, after `*rootView` is created. Add this line
    * `[RNBranch initSessionWithLaunchOptions:launchOptions isReferrable:YES];`
* Copy below method to same file if not already created

    ```objC
        - (BOOL)application:(UIApplication *)application continueUserActivity:(NSUserActivity *)userActivity restorationHandler:(void (^)(NSArray *restorableObjects))restorationHandler {
            return [RNBranch continueUserActivity:userActivity];
        }
    ```

* Other steps that must be done are defined more clearly [here](https://help.branch.io/developers-hub/docs/react-native#configure-app)

* Optionally, you can add general Aries deep link domain to be compatible with other applications: `didcomm`.

### Add custom font

By default ios app uses `System` font which is usually `San Francisco` on ios. If you want to add a custom font, then use below steps. Below steps are describing how to add `Lato` font. You can add any other font in similar way.

1. Add `Lato` fonts to Xcode project located here: `node_modules/@evernym/react-native-white-label-app/src/fonts/Lato` and update `info.plist` with configuration related to fonts:

    ```xml
        <key>UIAppFonts</key>
        <array>
            <string>Lato-Bold.ttf</string>
            <string>Lato-BoldItalic.ttf</string>
            <string>Lato-Italic.ttf</string>
            <string>Lato-Medium.ttf</string>
            <string>Lato-MediumItalic.ttf</string>
            <string>Lato-Regular.ttf</string>
            <string>Lato-Semibold.ttf</string>
            <string>Lato-SemiboldItalic.ttf</string>
        </array>
    ```

   In case you already added custom fonts to Xcode project, just expand list by adding Lato fonts.

## Issues

* **Building the app fails on XCode 12.5+**

  Adding those two blocks into your application Podfile file should resolve the issue:

  * after the section containing `source` statements:

    ```ruby
    def find_and_replace(dir, findstr, replacestr)
      Dir[dir].each do |name|
          text = File.read(name)
          replace = text.gsub(findstr,replacestr)
          if text != replace
              puts "Fix: " + name
              File.open(name, "w") { |file| file.puts replace }
              STDOUT.flush
          end
      end
      Dir[dir + '*/'].each(&method(:find_and_replace))
    end
    ```

  * inside the `post_install` hook before `end` keyword, add below code

    ```ruby
    find_and_replace("../node_modules/react-native/React/CxxBridge/RCTCxxBridge.mm",
    "_initializeModules:(NSArray<id<RCTBridgeModule>> *)modules", "_initializeModules:(NSArray<Class> *)modules")
    find_and_replace("../node_modules/react-native/ReactCommon/turbomodule/core/platform/ios/RCTTurboModuleManager.mm",
    "RCTBridgeModuleNameForClass(module))", "RCTBridgeModuleNameForClass(Class(module)))")
    ```

* **Missing ObjectiveC**

  Make sure you added .swift file and bridging header to your Xcode project, as instructed in this documentation.

  In case you experience this error:\
  `ld: warning: Could not find auto-linked library` please add next line in Build Settings, Search Library paths (in Xcode):

    ```objC
        $(TOOLCHAIN_DIR)/usr/lib/swift/$(PLATFORM_NAME)
    ```

* **Missing FS in DotEnv library**

  In case you experience issue with missing fs library `node_modules/react-native-dotenv/index.js`, this can be resolution:

  1. Add react-native-fs using yarn or npm
  2. Open DotEnv library in /node_modules/dotenv/lib/main.js
  3. Replace const `fs = require('fs')` to `fs = require('react-native-fs')`

  > Note: Unfortunately, if you rebuild node_modules, same steps will be necessary again, just to keep in mind.

* **vcx.framework/vcx' does not contain bitcode** *

  In case you experience issue with vcx or react-native-white-label-app pod `vcx.framework/vcx' does not contain bitcode`, this can be resolution:

  1. Open project in XCode and set `Bitcode=NO` for target pods.
  1. Add following lines to your app Podfile:
  
    ```ruby
        post_install do |installer|
            installer.pods_project.build_configurations.each do |config|
                config.build_settings["EXCLUDED_ARCHS[sdk=iphonesimulator*]"] = "arm64"
            end
            installer.pods_project.targets.each do |target|
                if target.name == "react-native-white-label-app"
                    target.build_configurations.each do |config|
                        config.build_settings['ENABLE_BITCODE'] = 'NO'
                    end
                end
                if target.name == "evernym-react-native-sdk"
                    target.build_configurations.each do |config|
                        config.build_settings['ENABLE_BITCODE'] = 'NO'
                    end
                end
                if target.name == "vcx"
                    target.build_configurations.each do |config|
                        config.build_settings['ENABLE_BITCODE'] = 'NO'
                    end
                end
            end
        end
    ```

* App builds fine, but at runtime we see error `No permission handler detected`. Add a `pre_install` hook

  * ```ruby
        pre_install do |installer|
            Pod::Installer::Xcode::TargetValidator.send(:define_method, :verify_no_static_framework_transitive_dependencies) {}

            installer.pod_targets.each do |pod|
                if pod.name.eql?('RNPermissions') || pod.name.start_with?('Permission-')
                    def pod.build_type;
                        # Uncomment the line corresponding to your CocoaPods version
                        Pod::BuildType.static_library # >= 1.9
                        # Pod::Target::BuildType.static_library # < 1.9
                    end
                end
            end
        end
    ```

  * Add permission handler for Camera. Put below code inside target of Podfile

    ```ruby
        # react-native-permissions permission handlers
        permissions_path = '../node_modules/react-native-permissions/ios'

        pod 'Permission-Camera', :path => "#{permissions_path}/Camera.podspec"
        pod 'Permission-FaceID', :path => "#{permissions_path}/FaceID.podspec"
        pod 'Permission-Microphone', :path => "#{permissions_path}/Microphone.podspec"
        pod 'Permission-PhotoLibrary', :path => "#{permissions_path}/PhotoLibrary.podspec"
    ```

* App build fails due to transitive statically linked Flipper libraries
  * For now, we don't support Flipper. Please disable Flipper by commenting this line (`# use_flipper!()`) in Podfile
