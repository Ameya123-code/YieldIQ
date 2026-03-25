# YieldSense 🌾

A modern, AI-powered crop yield estimation and analysis dashboard built with Streamlit. Get intelligent recommendations for optimal crop planting based on historical data, without machine learning complexity.

![YieldSense Dashboard](https://img.shields.io/badge/Streamlit-App-blue) ![Python](https://img.shields.io/badge/Python-3.8+-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

## 🚀 Features

### Core Functionality
- **Smart Crop Recommendations**: Get top 3 crops to plant based on historical yield trends
- **Yield Prediction**: Estimate production for any area using trend analysis
- **Peer Analysis**: Compare crop performance against regional averages
- **Interactive Charts**: Beautiful Altair visualizations for trend analysis
- **Data-Driven Insights**: Stability analysis and confidence metrics

### Advanced Features
- **Dynamic Filtering**: State, season, and time horizon selection
- **Real-time Calculations**: Trend-based predictions using polynomial fitting
- **Data Quality**: Automatic preprocessing with outlier removal
- **User-Friendly Interface**: Clean SaaS-style dashboard design
- **Database Management**: Add new records directly through the app

## 📊 Dashboard Sections

### Left Panel
- **Filters**: State, Season, Crop, Time Horizon, Area
- **Yield Prediction**: Direct estimates for selected parameters
- **Key Metrics**: Best and worst performing crops
- **Season Information**: Reference table for Kharif/Rabi/Zaid seasons

### Right Panel
- **Normalized Yield Trends**: Multi-crop comparison charts
- **Top 3 Crops**: Ranked recommendations with explanations
- **Individual Analysis**: Crop vs peer average with delta charts
- **Raw Data**: Complete dataset view

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Visualization**: Altair
- **Styling**: Custom CSS
- **Version Control**: Git
- **Deployment**: Ready for Streamlit Cloud

## 📋 Prerequisites

- Python 3.8 or higher
- Internet connection for data loading

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Ameya123-code/YieldIQ.git
   cd yieldsense
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Access the app**
   - Open http://localhost:8501 in your browser

## 📖 Usage Guide

### Basic Workflow
1. **Select State**: Choose from available Indian states
2. **Choose Season**: Kharif, Rabi, or Zaid (filtered by data availability)
3. **Set Time Horizon**: 1, 3, 5, 10 years, or all historical data
4. **Specify Area**: Enter land area in hectares
5. **Optional Crop**: Select specific crop or leave as "All"
6. **View Results**: Get predictions, recommendations, and analysis

### Adding New Data
- Use the expandable "Add new record to database" section
- Fill in State, District, Crop, Season, Year, Area, Production
- Click "Add record" to append to the dataset

### Understanding Results
- **Yield Prediction**: Trend-based estimate for your area
- **Top 3 Crops**: Ranked by predicted yield with stability notes
- **Charts**: Normalized trends and peer comparisons
- **Insights**: Plain-language explanations of recommendations

## 📊 Data Sources

- Historical crop production data from Indian agriculture datasets
- Covers multiple states, districts, crops, and seasons
- Preprocessed for quality: outlier removal, duplicate elimination

## 🔧 Configuration

### Environment Variables
No environment variables required for basic usage.

### Data Path
Dataset location: `data/crop_production.csv`
Modify `DATA_PATH` in `app.py` if needed.

### Customization
- Seasons: Edit the `seasons` list in `app.py`
- UI Colors: Modify CSS in the `css` variable
- Chart Themes: Adjust Altair chart configurations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Indian agriculture data sources
- Streamlit community for inspiration
- Open-source data visualization libraries

## 📞 Support

For questions or issues:
- Open an issue on GitHub
- Check the documentation
- Review the code comments

## 🔄 Future Enhancements

- [ ] Weather data integration
- [ ] Multi-language support
- [ ] Advanced ML models
- [ ] Mobile-responsive design
- [ ] API endpoints
- [ ] Batch data upload

---

**Made with ❤️ for farmers and agricultural analysts**

*Empowering data-driven farming decisions*