# Salary Transparency - Android App

An Android application for collecting and visualizing salary data, promoting transparency in compensation across industries.

## Features

- 📊 **Data Collection**: Submit salary information including job title, company, industry, salary, experience, and more
- 📈 **Visualizations**: Interactive charts showing salary distributions by industry, experience, education, and demographics
- 🔍 **Filtering**: Filter salary data by multiple criteria
- 💾 **Data Persistence**: Local database storage using Room
- 📤 **Export/Import**: CSV export and import functionality
- 🎨 **Material Design**: Modern UI following Material Design 3 guidelines
- 📱 **Mobile-First**: Optimized for Android devices

## Technical Stack

- **Language**: Kotlin
- **Minimum SDK**: Android 8.0 (API 26)
- **Target SDK**: Android 14 (API 35)
- **Architecture**: MVVM (Model-View-ViewModel)
- **Database**: Room Persistence Library
- **Charts**: MPAndroidChart
- **UI**: Material Design Components 3

## Dependencies

- AndroidX Core KTX 1.15.0
- AndroidX AppCompat 1.7.0
- Material Components 1.12.0
- Room Database 2.6.1
- Lifecycle Components 2.8.7
- Coroutines 1.9.0
- MPAndroidChart 3.1.0
- OpenCSV 5.9
- Gson 2.11.0

## Project Structure

```
app/src/main/java/com/salarytransparency/
├── data/
│   ├── dao/              # Data Access Objects
│   ├── database/         # Room Database
│   └── model/            # Data models
├── repository/           # Repository layer
├── viewmodel/            # ViewModels
├── ui/
│   ├── adapters/         # RecyclerView adapters
│   ├── fragments/        # UI fragments
│   └── MainActivity.kt   # Main activity
└── utils/                # Utility classes
```

## Setup Instructions

### Prerequisites

- Android Studio Otter | 2025.2.1 or later
- JDK 17 or later
- Android SDK with API 35
- Gradle 8.7.3 or later

### Opening the Project

1. Open Android Studio
2. Click "Open" and navigate to the `android-app` folder
3. Wait for Gradle sync to complete
4. Build the project (Build → Make Project)

### Running the App

1. Connect an Android device or start an emulator
2. Click "Run" (Shift+F10) or the green play button
3. Select your target device
4. The app will install and launch

### Building APK

```bash
# Debug APK
gradlew assembleDebug

# Release APK
gradlew assembleRelease
```

APKs will be in `app/build/outputs/apk/`

## Usage

### Submitting Salary Data

1. Tap the floating action button (+) or navigate to "Submit Salary"
2. Fill in the required fields:
   - Job Title (required)
   - Company (required)
   - Salary (required)
   - Years of Experience (required)
3. Fill in optional fields for more detailed insights
4. Tap "Submit"

### Viewing Visualizations

1. Navigate to "Visualizations" from the menu
2. View charts showing:
   - Salary distribution by industry
   - Salary trends by experience level
   - Gender distribution
   - Industry distribution

### Exporting Data

1. Navigate to "Export Data" from the menu
2. Choose a location to save the CSV file
3. Data will be exported in CSV format

### Importing Data

1. Navigate to "Export Data" from the menu
2. Tap "Import from CSV"
3. Select a CSV file with the correct format
4. Data will be imported into the database

## CSV Format

The app uses the following CSV format:

```csv
Job Title,Company,Industry,Currency,Salary,Salary USD,Years of Experience,Education Level,Location,Country,Nationality,Gender,Age,Benefits
```

## Database Schema

### SalaryEntry Table

| Column             | Type    | Description                    |
|--------------------|---------|--------------------------------|
| id                 | Long    | Primary key (auto-generated)   |
| jobTitle           | String  | Job title                      |
| company            | String  | Company name                   |
| industry           | String  | Industry sector                |
| currency           | String  | Salary currency                |
| salary             | Double  | Salary in original currency    |
| salaryUsd          | Double  | Salary converted to USD        |
| yearsOfExperience  | Int     | Years of professional experience|
| educationLevel     | String  | Highest education level        |
| location           | String  | City/location                  |
| country            | String  | Country                        |
| nationality        | String  | Nationality                    |
| gender             | String  | Gender                         |
| age                | Int     | Age                            |
| benefits           | String  | Additional benefits            |
| submissionDate     | Long    | Timestamp of submission        |

## Configuration

### Gradle Version

This project uses:
- Gradle 8.7.3
- Android Gradle Plugin 8.7.3
- Kotlin 2.1.0
- KSP 2.1.0-1.0.29

### Build Configuration

Edit `app/build.gradle.kts` to modify:
- Minimum SDK version
- Target SDK version
- Application ID
- Version code/name

## Troubleshooting

### Gradle Sync Issues

If Gradle sync fails:
1. File → Invalidate Caches → Invalidate and Restart
2. Delete `.gradle` folder in project root
3. Sync project again

### MPAndroidChart Repository

The project uses JitPack for MPAndroidChart. If sync fails, ensure `settings.gradle.kts` includes:

```kotlin
maven { url = uri("https://jitpack.io") }
```

### Build Errors

If you encounter build errors:
1. Clean project: Build → Clean Project
2. Rebuild: Build → Rebuild Project
3. Check Android SDK is properly installed

## License

This project is part of the Salary Transparency Platform.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Privacy

All salary data is stored locally on the device. No data is transmitted to external servers unless explicitly exported by the user.

## Future Enhancements

- [ ] Cloud sync support
- [ ] Advanced filtering options
- [ ] More chart types
- [ ] Dark mode support
- [ ] Multi-language support
- [ ] Real-time currency conversion API
- [ ] Salary comparison tools
- [ ] Anonymous data sharing (opt-in)
