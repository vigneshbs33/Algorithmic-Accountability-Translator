"""
Recommendation Pattern Analysis.

Uses interpretable ML models to understand and predict
recommendation algorithm behavior.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Any
import logging

try:
    import numpy as np
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.preprocessing import LabelEncoder, StandardScaler
    from sklearn.metrics import classification_report, accuracy_score
    import xgboost as xgb
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False


logger = logging.getLogger(__name__)


@dataclass
class FeatureImportance:
    """Feature importance from the model."""
    feature_name: str
    importance_score: float
    direction: str  # "positive", "negative", or "mixed"
    description: str


@dataclass
class PatternAnalysisResult:
    """Result of recommendation pattern analysis."""
    accuracy: float
    cross_val_accuracy: float
    feature_importances: List[FeatureImportance]
    
    # Key findings
    top_predictors: List[str]  # Features that most influence recommendations
    engagement_correlation: float  # How much engagement drives recommendations
    diversity_penalty: float  # How much diverse content is penalized
    
    # Model details
    model_type: str
    num_samples: int
    num_features: int


@dataclass
class RecommendationPrediction:
    """Prediction for a single content item."""
    content_id: str
    will_be_recommended: bool
    probability: float
    contributing_factors: List[Tuple[str, float]]


class RecommendationPatternAnalyzer:
    """
    Analyzes recommendation patterns using interpretable ML.
    
    Trains models to predict what content gets recommended and
    uses feature importance to understand algorithm behavior.
    """
    
    def __init__(self, model_type: str = "random_forest"):
        """
        Initialize pattern analyzer.
        
        Args:
            model_type: Type of model - "random_forest" or "xgboost".
        """
        if not ML_AVAILABLE:
            raise ImportError(
                "Required libraries not installed. "
                "Run: pip install numpy pandas scikit-learn xgboost"
            )
        
        self.model_type = model_type
        self._model = None
        self._feature_names = None
        self._label_encoders = {}
        self._scaler = StandardScaler()
    
    def prepare_features(
        self,
        content_data: List[Dict]
    ) -> Tuple[np.ndarray, List[str]]:
        """
        Prepare features from content data.
        
        Args:
            content_data: List of content dictionaries with various attributes.
            
        Returns:
            Tuple of (feature matrix, feature names).
        """
        # Define features to extract
        feature_defs = {
            # Engagement features
            "upvotes": lambda x: x.get("upvotes", 0),
            "comments_count": lambda x: x.get("comments_count", 0),
            "views_count": lambda x: x.get("views_count", 0),
            
            # Content features
            "title_length": lambda x: len(x.get("title", "")),
            "body_length": lambda x: len(x.get("body", "")),
            "has_video": lambda x: 1 if x.get("is_video", False) else 0,
            "has_image": lambda x: 1 if x.get("thumbnail_url") else 0,
            
            # Timing features
            "hour_posted": lambda x: x.get("created_at").hour if x.get("created_at") else 12,
            "day_of_week": lambda x: x.get("created_at").weekday() if x.get("created_at") else 3,
            
            # Engagement ratios
            "engagement_rate": lambda x: (
                (x.get("upvotes", 0) + x.get("comments_count", 0)) / 
                max(1, x.get("views_count", 1))
            ),
            
            # Sentiment/bias scores (if available)
            "sensationalism_score": lambda x: x.get("sensationalism_score", 0.5),
            "bias_score": lambda x: x.get("composite_bias_score", 0.5),
            
            # Position/context
            "is_top_of_feed": lambda x: 1 if x.get("rank", 100) <= 5 else 0,
        }
        
        # Extract features
        features = []
        for item in content_data:
            row = []
            for name, extractor in feature_defs.items():
                try:
                    value = extractor(item)
                    row.append(float(value) if value is not None else 0.0)
                except:
                    row.append(0.0)
            features.append(row)
        
        self._feature_names = list(feature_defs.keys())
        return np.array(features), self._feature_names
    
    def train(
        self,
        content_data: List[Dict],
        labels: List[int],  # 1 = recommended, 0 = not recommended
        test_size: float = 0.2
    ) -> PatternAnalysisResult:
        """
        Train model to predict recommendation patterns.
        
        Args:
            content_data: List of content dictionaries.
            labels: Binary labels indicating if content was recommended.
            test_size: Proportion of data for testing.
            
        Returns:
            PatternAnalysisResult with model performance and insights.
        """
        # Prepare features
        X, feature_names = self.prepare_features(content_data)
        y = np.array(labels)
        
        # Scale features
        X_scaled = self._scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=test_size, random_state=42
        )
        
        # Train model
        if self.model_type == "xgboost":
            self._model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
        else:
            self._model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
        
        self._model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self._model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Cross-validation
        cv_scores = cross_val_score(self._model, X_scaled, y, cv=5)
        cv_accuracy = cv_scores.mean()
        
        # Feature importances
        importances = self._model.feature_importances_
        feature_importance_list = []
        
        for name, importance in zip(feature_names, importances):
            # Determine direction based on correlation with positive class
            mask = y == 1
            if X[:, feature_names.index(name)][mask].mean() > X[:, feature_names.index(name)][~mask].mean():
                direction = "positive"
            else:
                direction = "negative"
            
            feature_importance_list.append(FeatureImportance(
                feature_name=name,
                importance_score=importance,
                direction=direction,
                description=self._get_feature_description(name, direction)
            ))
        
        # Sort by importance
        feature_importance_list.sort(key=lambda x: x.importance_score, reverse=True)
        
        # Calculate specific metrics
        engagement_features = ["upvotes", "comments_count", "views_count", "engagement_rate"]
        engagement_importance = sum(
            fi.importance_score for fi in feature_importance_list
            if fi.feature_name in engagement_features
        )
        
        diversity_penalty = 1 - (
            next(
                (fi.importance_score for fi in feature_importance_list 
                 if fi.feature_name == "bias_score"),
                0.1
            )
        )
        
        return PatternAnalysisResult(
            accuracy=accuracy,
            cross_val_accuracy=cv_accuracy,
            feature_importances=feature_importance_list,
            top_predictors=[fi.feature_name for fi in feature_importance_list[:5]],
            engagement_correlation=engagement_importance,
            diversity_penalty=diversity_penalty,
            model_type=self.model_type,
            num_samples=len(content_data),
            num_features=len(feature_names)
        )
    
    def predict(
        self,
        content_data: List[Dict]
    ) -> List[RecommendationPrediction]:
        """
        Predict which content will be recommended.
        
        Args:
            content_data: List of content dictionaries.
            
        Returns:
            List of predictions with probabilities.
        """
        if self._model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        X, _ = self.prepare_features(content_data)
        X_scaled = self._scaler.transform(X)
        
        probabilities = self._model.predict_proba(X_scaled)[:, 1]
        predictions = self._model.predict(X_scaled)
        
        results = []
        for i, (item, prob, pred) in enumerate(zip(content_data, probabilities, predictions)):
            # Get feature contributions (simplified without SHAP)
            contributions = []
            for j, name in enumerate(self._feature_names):
                importance = self._model.feature_importances_[j]
                value = X[i, j]
                contributions.append((name, importance * value))
            
            contributions.sort(key=lambda x: abs(x[1]), reverse=True)
            
            results.append(RecommendationPrediction(
                content_id=item.get("content_id", str(i)),
                will_be_recommended=bool(pred),
                probability=float(prob),
                contributing_factors=contributions[:5]
            ))
        
        return results
    
    def _get_feature_description(self, feature_name: str, direction: str) -> str:
        """Get human-readable description of feature effect."""
        descriptions = {
            "upvotes": {
                "positive": "Content with more upvotes is more likely to be recommended",
                "negative": "Content with fewer upvotes is more likely to be recommended"
            },
            "comments_count": {
                "positive": "Content with more comments is more likely to be recommended",
                "negative": "Content with fewer comments is more likely to be recommended"
            },
            "sensationalism_score": {
                "positive": "More sensational content is more likely to be recommended",
                "negative": "Less sensational content is more likely to be recommended"
            },
            "bias_score": {
                "positive": "More biased content is more likely to be recommended",
                "negative": "More neutral content is more likely to be recommended"
            },
            "engagement_rate": {
                "positive": "Higher engagement rate leads to more recommendations",
                "negative": "Lower engagement rate leads to more recommendations"
            }
        }
        
        default = {
            "positive": f"Higher {feature_name} correlates with recommendation",
            "negative": f"Lower {feature_name} correlates with recommendation"
        }
        
        return descriptions.get(feature_name, default).get(direction, "")
    
    def get_shap_explanation(
        self,
        content_data: List[Dict],
        max_display: int = 10
    ) -> Dict[str, Any]:
        """
        Get SHAP-based feature explanations.
        
        Returns:
            Dictionary with SHAP values and summary.
        """
        if not SHAP_AVAILABLE:
            return {"error": "SHAP not installed. Run: pip install shap"}
        
        if self._model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        X, _ = self.prepare_features(content_data)
        X_scaled = self._scaler.transform(X)
        
        # Calculate SHAP values
        explainer = shap.TreeExplainer(self._model)
        shap_values = explainer.shap_values(X_scaled)
        
        # Aggregate feature importance
        if isinstance(shap_values, list):
            shap_values = shap_values[1]  # For binary classification
        
        mean_abs_shap = np.abs(shap_values).mean(axis=0)
        
        feature_shap = [
            (name, float(score))
            for name, score in zip(self._feature_names, mean_abs_shap)
        ]
        feature_shap.sort(key=lambda x: x[1], reverse=True)
        
        return {
            "top_features": feature_shap[:max_display],
            "shap_values": shap_values.tolist(),
            "feature_names": self._feature_names
        }
