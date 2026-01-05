import torch
import torch.nn as nn
from sklearn.preprocessing import StandardScaler
import numpy as np

class Autoencoder(nn.Module):
    def __init__(self, input_dim, encoding_dim=8):
        super(Autoencoder, self).__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 16),
            nn.ReLU(),
            nn.Linear(16, encoding_dim),
            nn.ReLU()
        )
        self.decoder = nn.Sequential(
            nn.Linear(encoding_dim, 16),
            nn.ReLU(),
            nn.Linear(16, input_dim),
            nn.Sigmoid() # Or nn.ReLU() depending on normalization
        )

    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded

class AutoencoderAnomalyModel(AnomalyDetectionModel):
    def __init__(self, model_path="path/to/your/trained_autoencoder.pth", input_dim=25):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = Autoencoder(input_dim=input_dim).to(self.device)
        # self.model.load_state_dict(torch.load(model_path)) # Uncomment after training
        self.model.eval()
        self.scaler = StandardScaler() # Fit this scaler on your training data

    def predict(self, features_df: pd.DataFrame) -> np.ndarray:
        # Assuming features_df is already numeric
        scaled_data = self.scaler.transform(features_df)
        data_tensor = torch.FloatTensor(scaled_data).to(self.device)
        
        with torch.no_grad():
            reconstructions = self.model(data_tensor)
            loss = nn.MSELoss(reduction='none')(reconstructions, data_tensor)
            reconstruction_error = torch.mean(loss, dim=1).cpu().numpy()
            
        # Higher error means more anomalous. You might need to scale this to a 0-1 range.
        anomaly_scores = (reconstruction_error - np.min(reconstruction_error)) / (np.max(reconstruction_error) - np.min(reconstruction_error))
        return anomaly_scores
