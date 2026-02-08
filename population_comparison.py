# 📊 POPULATION COMPARISON MODE
# Compare individual diagnosis with population statistics and epidemiology

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random

# Population statistics database
POPULATION_STATISTICS = {
    "Pneumonia": {
        "global_prevalence": 0.15,  # 15% of population
        "annual_cases": 4000000,
        "mortality_rate": 5.5,  # Percentage
        "age_groups": {
            "0-18": {"prevalence": 22, "mortality": 1.2},
            "19-65": {"prevalence": 12, "mortality": 3.5},
            "65+": {"prevalence": 28, "mortality": 15.2}
        },
        "gender_ratio": {"male": 55, "female": 45},
        "seasonal_peak": "Winter",
        "recovery_rate": 94.5,
        "hospitalization_rate": 18,
        "risk_factors": {
            "smoking": 2.5,
            "diabetes": 1.8,
            "COPD": 3.2,
            "immunosuppression": 4.1
        }
    },
    "Brain Tumor": {
        "global_prevalence": 0.02,  # 2% of population
        "annual_cases": 296000,
        "mortality_rate": 25.0,
        "age_groups": {
            "0-18": {"prevalence": 5, "mortality": 30},
            "19-65": {"prevalence": 2, "mortality": 22},
            "65+": {"prevalence": 4, "mortality": 35}
        },
        "gender_ratio": {"male": 48, "female": 52},
        "seasonal_peak": "None",
        "recovery_rate": 72.5,
        "hospitalization_rate": 85,
        "risk_factors": {
            "radiation_exposure": 3.5,
            "family_history": 2.8,
            "immunosuppression": 2.5
        }
    },
    "Diabetic Retinopathy": {
        "global_prevalence": 0.08,
        "annual_cases": 2700000,
        "mortality_rate": 2.5,
        "age_groups": {
            "0-18": {"prevalence": 0.5, "mortality": 0.1},
            "19-65": {"prevalence": 8, "mortality": 2.0},
            "65+": {"prevalence": 20, "mortality": 5.5}
        },
        "gender_ratio": {"male": 52, "female": 48},
        "seasonal_peak": "None",
        "recovery_rate": 65.0,
        "hospitalization_rate": 5,
        "risk_factors": {
            "type_2_diabetes": 4.2,
            "hypertension": 2.1,
            "poor_glycemic_control": 3.8
        }
    },
    "Tuberculosis": {
        "global_prevalence": 0.23,
        "annual_cases": 10000000,
        "mortality_rate": 1.3,
        "age_groups": {
            "0-18": {"prevalence": 15, "mortality": 0.5},
            "19-65": {"prevalence": 25, "mortality": 1.2},
            "65+": {"prevalence": 18, "mortality": 3.5}
        },
        "gender_ratio": {"male": 65, "female": 35},
        "seasonal_peak": "Winter",
        "recovery_rate": 87.0,
        "hospitalization_rate": 25,
        "risk_factors": {
            "HIV_AIDS": 26.0,
            "malnutrition": 3.5,
            "smoking": 1.6,
            "alcohol_abuse": 3.3
        }
    },
    "Skin Cancer": {
        "global_prevalence": 0.05,
        "annual_cases": 1900000,
        "mortality_rate": 2.0,
        "age_groups": {
            "0-18": {"prevalence": 1, "mortality": 0.2},
            "19-65": {"prevalence": 5, "mortality": 1.5},
            "65+": {"prevalence": 12, "mortality": 4.8}
        },
        "gender_ratio": {"male": 52, "female": 48},
        "seasonal_peak": "Summer",
        "recovery_rate": 98.0,
        "hospitalization_rate": 2,
        "risk_factors": {
            "sun_exposure": 8.5,
            "fair_skin": 5.2,
            "family_history": 2.8,
            "age": 3.5
        }
    },
    "Malaria": {
        "global_prevalence": 0.04,
        "annual_cases": 250000000,
        "mortality_rate": 0.2,
        "age_groups": {
            "0-18": {"prevalence": 8, "mortality": 0.4},
            "19-65": {"prevalence": 3, "mortality": 0.1},
            "65+": {"prevalence": 2, "mortality": 0.3}
        },
        "gender_ratio": {"male": 50, "female": 50},
        "seasonal_peak": "Rainy Season",
        "recovery_rate": 99.8,
        "hospitalization_rate": 3,
        "risk_factors": {
            "endemic_area": 20.0,
            "no_preventive_meds": 5.5,
            "mosquito_exposure": 4.2
        }
    },
    "Dental": {
        "global_prevalence": 0.30,
        "annual_cases": 11000000,
        "mortality_rate": 0.001,
        "age_groups": {
            "0-18": {"prevalence": 25, "mortality": 0.0},
            "19-65": {"prevalence": 30, "mortality": 0.001},
            "65+": {"prevalence": 35, "mortality": 0.01}
        },
        "gender_ratio": {"male": 48, "female": 52},
        "seasonal_peak": "None",
        "recovery_rate": 99.9,
        "hospitalization_rate": 0.1,
        "risk_factors": {
            "poor_hygiene": 3.2,
            "sugar_consumption": 2.8,
            "smoking": 1.9
        }
    }
}


class PopulationComparisonEngine:
    """Compare individual diagnosis with population statistics"""
    
    def __init__(self):
        self.population_data = POPULATION_STATISTICS
    
    def get_population_stats(self, disease: str, age: int = None, 
                            gender: str = None) -> dict:
        """Get population statistics for disease"""
        
        if disease not in self.population_data:
            return {"error": f"No population data for {disease}"}
        
        global_stats = self.population_data[disease].copy()
        
        # If age specified, get age-group specific data
        if age is not None:
            age_group = self._get_age_group(age)
            if age_group in global_stats.get("age_groups", {}):
                age_data = global_stats["age_groups"][age_group]
                global_stats["patient_age_group"] = age_group
                global_stats["age_specific_prevalence"] = age_data["prevalence"]
                global_stats["age_specific_mortality"] = age_data["mortality"]
        
        return global_stats
    
    def _get_age_group(self, age: int) -> str:
        """Determine age group from age"""
        if age < 19:
            return "0-18"
        elif age < 66:
            return "19-65"
        else:
            return "65+"
    
    def calculate_risk_percentile(self, disease: str, individual_score: float,
                                 age: int = None) -> dict:
        """Calculate where patient falls in population distribution"""
        
        stats = self.get_population_stats(disease, age)
        
        # Simulate population distribution (normal distribution)
        mean_score = 45
        std_dev = 15
        
        # Calculate percentile
        from scipy import stats as sp_stats
        percentile = sp_stats.norm.cdf(individual_score, mean_score, std_dev) * 100
        
        # Risk category
        if percentile >= 90:
            risk_category = "Very High Risk (Top 10%)"
        elif percentile >= 75:
            risk_category = "High Risk (Top 25%)"
        elif percentile >= 50:
            risk_category = "Above Average Risk"
        elif percentile >= 25:
            risk_category = "Moderate Risk"
        else:
            risk_category = "Low Risk"
        
        return {
            "percentile": percentile,
            "risk_category": risk_category,
            "population_mean": mean_score,
            "individual_score": individual_score,
            "comparison": "Higher" if individual_score > mean_score else "Lower"
        }
    
    def get_epidemic_status(self, disease: str) -> dict:
        """Get epidemic/endemic status information"""
        
        if disease not in self.population_data:
            return {"error": "Unknown disease"}
        
        stats = self.population_data[disease]
        
        # Simulate trend data
        months = 12
        trend = [
            100 + random.randint(-20, 30) 
            for _ in range(months)
        ]
        
        trend_direction = "increasing" if trend[-1] > trend[0] else "decreasing"
        
        return {
            "disease": disease,
            "trend_direction": trend_direction,
            "trend_data": trend,
            "seasonal_peak": stats.get("seasonal_peak"),
            "current_cases": stats.get("annual_cases"),
            "outbreak_status": "Endemic" if stats.get("global_prevalence", 0) > 0.1 else "Sporadic"
        }


def show_population_comparison(disease: str, confidence: float, 
                               age: int = None, gender: str = None):
    """Display population comparison interface"""
    
    st.markdown("### 📊 Population Comparison Analysis")
    st.info(
        "Compare your diagnosis with population-wide statistics "
        "and epidemiological data"
    )
    
    engine = PopulationComparisonEngine()
    
    # Get population stats
    pop_stats = engine.get_population_stats(disease, age, gender)
    
    if "error" in pop_stats:
        st.warning(f"⚠️ {pop_stats['error']}")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Global Prevalence",
            f"{pop_stats['global_prevalence']*100:.1f}%",
            "of population"
        )
    
    with col2:
        st.metric(
            "Annual Cases",
            f"{pop_stats['annual_cases']:,}",
            "worldwide"
        )
    
    with col3:
        st.metric(
            "Mortality Rate",
            f"{pop_stats['mortality_rate']:.1f}%",
            "among cases"
        )
    
    with col4:
        st.metric(
            "Recovery Rate",
            f"{pop_stats['recovery_rate']:.1f}%",
            "with treatment"
        )
    
    st.markdown("---")
    
    # Patient risk assessment
    if age:
        st.markdown("### 🎯 Personalized Risk Assessment")
        
        risk_analysis = engine.calculate_risk_percentile(disease, confidence, age)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.metric(
                "Risk Percentile",
                f"{risk_analysis['percentile']:.1f}th",
                risk_analysis['risk_category']
            )
        
        with col2:
            comparison = (
                f"↑ {abs(risk_analysis['individual_score'] - risk_analysis['population_mean']):.1f}% "
                f"{'above' if risk_analysis['comparison'] == 'Higher' else 'below'} population average"
            )
            st.metric("vs Population", "Average", comparison)
        
        st.markdown("---")
    
    # Demographics comparison
    st.markdown("### 👥 Demographics Comparison")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.write("**Age Group Distribution:**")
        
        age_data = pop_stats.get("age_groups", {})
        age_labels = list(age_data.keys())
        age_prevalence = [age_data[ag]["prevalence"] for ag in age_labels]
        
        fig = px.bar(
            x=age_labels,
            y=age_prevalence,
            labels={"x": "Age Group", "y": "Prevalence (%)"},
            title="Disease Prevalence by Age"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.write("**Gender Distribution:**")
        
        gender_data = pop_stats.get("gender_ratio", {})
        
        fig = go.Figure(data=[
            go.Pie(
                labels=list(gender_data.keys()),
                values=list(gender_data.values()),
                title="Gender Distribution"
            )
        ])
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Risk factors analysis
    st.markdown("### ⚠️ Risk Factor Analysis")
    
    risk_factors = pop_stats.get("risk_factors", {})
    
    if risk_factors:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.write("**Top Risk Factors:**")
            
            sorted_factors = sorted(
                risk_factors.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            for factor, multiplier in sorted_factors[:5]:
                risk_level = "🔴" if multiplier > 3 else "🟡" if multiplier > 1.5 else "🟢"
                st.write(
                    f"{risk_level} **{factor.replace('_', ' ').title()}**: "
                    f"{multiplier}x risk"
                )
        
        with col2:
            st.write("**Risk Factor Impact:**")
            
            factor_names = [f.replace('_', ' ').title() for f in risk_factors.keys()]
            factor_values = list(risk_factors.values())
            
            fig = px.bar(
                x=factor_names,
                y=factor_values,
                labels={"x": "Risk Factor", "y": "Risk Multiplier"},
                title="Risk Factor Severity"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Epidemic status
    st.markdown("### 🌍 Epidemic Status & Trends")
    
    epidemic_data = engine.get_epidemic_status(disease)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Seasonal Peak",
            epidemic_data['seasonal_peak'],
            "highest incidence"
        )
    
    with col2:
        st.metric(
            "Status",
            epidemic_data['outbreak_status'],
            "geographic distribution"
        )
    
    with col3:
        st.metric(
            "Trend",
            "📈 Increasing" if epidemic_data['trend_direction'] == "increasing" else "📉 Decreasing",
            "cases over time"
        )
    
    # Trend visualization
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        y=epidemic_data['trend_data'],
        mode='lines+markers',
        name='Incident Cases',
        line=dict(color='rgb(0, 212, 170)', width=3)
    ))
    
    fig.update_layout(
        title="12-Month Disease Trend",
        xaxis_title="Month",
        yaxis_title="Relative Incidence",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Comparative outcomes
    st.markdown("### 📈 Comparative Outcomes")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.write("**Treatment Outcomes:**")
        
        outcomes = {
            "Recovery": pop_stats['recovery_rate'],
            "Hospitalization": pop_stats['hospitalization_rate'],
            "Mortality": pop_stats['mortality_rate']
        }
        
        fig = px.bar(
            x=list(outcomes.keys()),
            y=list(outcomes.values()),
            color=list(outcomes.keys()),
            labels={"x": "Outcome", "y": "Percentage (%)"},
            title="Population Outcomes"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.write("**Your vs Population:**")
        
        your_outcome = 100 - confidence  # Simplified
        
        comparison_data = {
            "You": confidence,
            "Population Avg": pop_stats['recovery_rate']
        }
        
        fig = go.Figure(data=[
            go.Bar(name='Your Outcome', x=['Your Prognosis'], y=[your_outcome]),
            go.Bar(name='Population Avg', x=['Population Average'], y=[pop_stats['recovery_rate']])
        ])
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Export comparison report
    st.markdown("#### 📥 Export Comparison Report")
    
    report = f"""
POPULATION COMPARISON REPORT
============================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

DISEASE: {disease}
=========

GLOBAL STATISTICS
=================
Prevalence: {pop_stats['global_prevalence']*100:.1f}% of population
Annual Cases: {pop_stats['annual_cases']:,}
Mortality Rate: {pop_stats['mortality_rate']:.1f}%
Recovery Rate: {pop_stats['recovery_rate']:.1f}%
Hospitalization Rate: {pop_stats['hospitalization_rate']:.1f}%

YOUR DIAGNOSIS
==============
AI Confidence: {confidence:.1f}%
"""
    
    if age:
        risk_analysis = engine.calculate_risk_percentile(disease, confidence, age)
        report += f"""
RISK ASSESSMENT
===============
Risk Percentile: {risk_analysis['percentile']:.1f}th
Risk Category: {risk_analysis['risk_category']}
Comparison: {risk_analysis['comparison']} population average by {abs(risk_analysis['individual_score'] - risk_analysis['population_mean']):.1f}%
"""
    
    st.download_button(
        label="📄 Download Comparison Report",
        data=report,
        file_name=f"population_comparison_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
        mime="text/plain"
    )