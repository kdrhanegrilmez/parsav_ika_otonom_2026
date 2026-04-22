#include <gazebo/gazebo.hh>
#include <gazebo/physics/physics.hh>
#include <gazebo/common/common.hh>
#include <ignition/math/Vector3.hh>

namespace gazebo
{
  class SlidingObstaclePlugin : public ModelPlugin
  {
    public: void Load(physics::ModelPtr _parent, sdf::ElementPtr _sdf)
    {
      this->model = _parent;
      this->velocity = 0.2;
      this->range = 1.0;
      this->direction = 1;
      this->start_pos = this->model->WorldPose().Pos();

      if (_sdf->HasElement("velocity"))
        this->velocity = _sdf->Get<double>("velocity");
      if (_sdf->HasElement("range"))
        this->range = _sdf->Get<double>("range");

      this->updateConnection = event::Events::ConnectWorldUpdateBegin(
          std::bind(&SlidingObstaclePlugin::OnUpdate, this));
    }

    public: void OnUpdate()
    {
      ignition::math::Vector3d current_pos = this->model->WorldPose().Pos();
      
      // Y ekseninde hareket (Sağa sola kayma)
      if (std::abs(current_pos.Y() - this->start_pos.Y()) > this->range)
      {
        this->direction *= -1;
      }

      this->model->SetLinearVel(ignition::math::Vector3d(0, this->velocity * this->direction, 0));
    }

    private: physics::ModelPtr model;
    private: event::ConnectionPtr updateConnection;
    private: double velocity;
    private: double range;
    private: int direction;
    private: ignition::math::Vector3d start_pos;
  };

  GZ_REGISTER_MODEL_PLUGIN(SlidingObstaclePlugin)
}
