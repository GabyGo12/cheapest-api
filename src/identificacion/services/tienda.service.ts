import {
  Injectable,
  NotFoundException,
} from '@nestjs/common';
import { CreateTiendaDto, UpdateTiendaDto } from '../dtos';
import { TiendaRepository } from '../repositories';
import { Tienda } from '../repositories/entities';

@Injectable()
export class TiendaService {
  constructor(
    private readonly tiendaRepository: TiendaRepository,
  ) {}

  async create(dto: CreateTiendaDto): Promise<Tienda> {
    return this.tiendaRepository.create(dto);
  }

  async findAll(): Promise<Tienda[]> {
    return this.tiendaRepository.findAll();
  }

  async findById(id: string): Promise<Tienda> {
    const tienda = await this.tiendaRepository.findById(id);

    if (!tienda) {
      throw new NotFoundException(
        `Tienda con id ${id} no encontrada`,
      );
    }

    return tienda;
  }

  async update(
    id: string,
    dto: UpdateTiendaDto,
  ): Promise<Tienda> {
    const tienda = await this.tiendaRepository.findById(id);

    if (!tienda) {
      throw new NotFoundException(
        `Tienda con id ${id} no encontrada`,
      );
    }

    const updatedTienda = await this.tiendaRepository.update(
      id,
      dto,
    );

    return updatedTienda!;
  }

  async delete(id: string): Promise<void> {
    const tienda = await this.tiendaRepository.findById(id);

    if (!tienda) {
      throw new NotFoundException(
        `Tienda con id ${id} no encontrada`,
      );
    }

    await this.tiendaRepository.delete(id);
  }

  async exists(id: string): Promise<boolean> {
    const tienda = await this.tiendaRepository.findById(id);
    return !!tienda;
  }
}