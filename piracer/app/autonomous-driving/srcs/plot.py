# ------------------------------------------------------------------------------
# Third-party Library Import
import  seaborn as sns
import  matplotlib.pyplot as plt
from    sklearn.metrics \
        import  confusion_matrix, \
                classification_report

# ------------------------------------------------------------------------------
def plot_fit(history):
    # Learning curve visualize
    # - Loss Graph
    plt.figure(figsize=(12, 4))
    plt.subplot(1, 2, 1)
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.legend()
    plt.title('Loss Evolution')
    # - Accuracy Graph
    plt.subplot(1, 2, 2)
    plt.plot(history.history['accuracy'], label='Training Accuracy')
    plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
    plt.legend()
    plt.title('Accuracy Evolution')
    plt.tight_layout()
    plt.show()

def plot_predict(labels_actual, labels_predict, label_list):
    # Confusion Matrix Visualize
    confusion_mat   = confusion_matrix(
        labels_actual,
        labels_predict,
        labels=label_list
    )

    plt.figure(figsize=(8, 6))
    sns.heatmap(
        confusion_mat,
        annot=True,
        fmt='d',
        cmap='Blues',
        xticklabels=label_list,
        yticklabels=label_list
    )
    plt.xlabel('Predicted Labels')
    plt.ylabel('True Labels')
    plt.title('Confusion Matrix')
    plt.show()

    # Precision, Recall, F1-Score
    report = classification_report(
        labels_actual,
        labels_predict,
        target_names=label_list
    )
    print(report)