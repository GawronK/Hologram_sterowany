import cv2
import mediapipe as mp
import vtk
import numpy as np

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.5)

# Kamera
cap = cv2.VideoCapture(0)

stl_reader = vtk.vtkSTLReader()
stl_reader.SetFileName('rubber_duck.stl')
stl_reader.Update()

mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(stl_reader.GetOutputPort())
actor = vtk.vtkActor()
actor.SetMapper(mapper)

renderer = vtk.vtkRenderer()
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)
render_window_interactor = vtk.vtkRenderWindowInteractor()
render_window_interactor.SetRenderWindow(render_window)

renderer.AddActor(actor)
renderer.SetBackground(0.1, 0.1, 0.1)
render_window.Render()

last_pos = {"Left": (0, 0), "Right": (0, 0)}
first_frame = {"Left": True, "Right": True}
scale_factor = 1.0
min_scale = 0.2
max_scale = 3.0
damping = 0.002

def calculate_distance(landmark1, landmark2, width, height):
    return np.sqrt((landmark1.x * width - landmark2.x * width) ** 2 +
                   (landmark1.y * height - landmark2.y * height) ** 2)

def recognize_hand_gesture(hand_landmarks, width, height):
    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    middle_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    ring_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
    pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]

    thumb_wrist_dist = calculate_distance(wrist, thumb_tip, width, height)
    index_wrist_dist = calculate_distance(wrist, index_finger_tip, width, height)
    middle_wrist_dist = calculate_distance(wrist, middle_finger_tip, width, height)
    ring_wrist_dist = calculate_distance(wrist, ring_finger_tip, width, height)
    pinky_wrist_dist = calculate_distance(wrist, pinky_tip, width, height)

    thumb_index_dist = calculate_distance(thumb_tip, index_finger_tip, width, height)
    index_middle_dist = calculate_distance(index_finger_tip, middle_finger_tip, width, height)
    middle_ring_dist = calculate_distance(middle_finger_tip, ring_finger_tip, width, height)
    ring_pinky_dist = calculate_distance(ring_finger_tip, pinky_tip, width, height)

    fist_threshold = 0.2 * height
    open_hand_threshold = 0.3 * height

    if (index_wrist_dist < fist_threshold and
        middle_wrist_dist < fist_threshold and
        ring_wrist_dist < fist_threshold and
        pinky_wrist_dist < fist_threshold and
        thumb_index_dist < fist_threshold):
        return "Fist Closed"

    if (index_wrist_dist > open_hand_threshold and
        middle_wrist_dist > open_hand_threshold and
        ring_wrist_dist > open_hand_threshold and
        pinky_wrist_dist > open_hand_threshold and
        thumb_index_dist > open_hand_threshold and
        index_middle_dist > open_hand_threshold and
        middle_ring_dist > open_hand_threshold and
        ring_pinky_dist > open_hand_threshold):
        return "Hand Opened"

    return "Hand Opened"

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    gestures = {"Left": "No Hand", "Right": "No Hand"}

    if result.multi_hand_landmarks and result.multi_handedness:
        for idx, hand_landmarks in enumerate(result.multi_hand_landmarks):
            hand_label = result.multi_handedness[idx].classification[0].label
            width, height = frame.shape[1], frame.shape[0]
            gesture = recognize_hand_gesture(hand_landmarks, width, height)
            gestures[hand_label] = gesture

            wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
            current_x, current_y = wrist.x * width, wrist.y * height

            if not first_frame[hand_label]:
                delta_x = (current_x - last_pos[hand_label][0]) * damping
                delta_y = (current_y - last_pos[hand_label][1]) * damping

                if gesture == "Fist Closed" and hand_label == "Right":
                    actor.RotateX(delta_y * 180)
                    actor.RotateY(delta_x * 180)
                    render_window.Render()

                if gesture == "Fist Closed" and hand_label == "Left":
                    
                    scale_change = delta_x * 5  # czułość
                    scale_factor = max(min_scale, min(max_scale, scale_factor + scale_change))

                    actor.SetScale(scale_factor, scale_factor, scale_factor)
                    render_window.Render()

            last_pos[hand_label] = (current_x, current_y)
            first_frame[hand_label] = False

            mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.putText(frame, f'Left Hand: {gestures["Left"]}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f'Right Hand: {gestures["Right"]}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow('Hand Tracking', frame)
    render_window.Render()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
hands.close()
render_window_interactor.TerminateApp()
